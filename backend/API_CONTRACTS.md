# ClauseLens API Contracts

This document defines the communication contract between all six team members.
Every module integration is documented here so development can proceed independently.

---

## 1. Frontend ↔ Django Backend (Member 1 ↔ Member 2)

**Base URL:** `http://localhost:8000/api/`

**Authentication:** JWT Bearer token in `Authorization` header.

**Content-Type:** `application/json` for all requests except file uploads (`multipart/form-data`).

**Reference:** See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for full endpoint specifications.

**Key pages and their API calls:**

| Frontend Page | API Calls |
|---------------|-----------|
| Login / Register | `POST /api/auth/login/`, `POST /api/auth/register/` |
| Dashboard | `GET /api/dashboard/` |
| Document Upload | `POST /api/documents/upload/`, `POST /api/documents/url/` |
| My Documents | `GET /api/documents/` |
| Analysis Results | `GET /api/analysis/documents/{id}/clauses/`, `GET /api/analysis/documents/{id}/result/` |
| Risk Analysis | `GET /api/personalization/documents/{id}/risks/` |
| Profile | `GET/POST/PUT /api/profile/` |
| Policy Monitoring | `GET/POST /api/monitoring/` |
| Version History | `GET /api/versions/{document_id}/`, `GET /api/versions/{document_id}/compare/` |
| Notifications | `GET /api/notifications/`, `PATCH /api/notifications/read-all/` |

---

## 2. Django Backend ↔ PostgreSQL (Member 2 ↔ Member 3)

The Django ORM manages the database schema via migrations.

**Django models (Member 3 must review and coordinate):**

| Model | Table | App |
|-------|-------|-----|
| User | `users` | `apps.accounts` |
| UserProfile | `user_profiles` | `apps.profiles` |
| Document | `documents` | `apps.documents` |
| Clause | `clauses` | `apps.analysis` |
| AnalysisResult | `analysis_results` | `apps.analysis` |
| PersonalizedRisk | `personalized_risks` | `apps.personalization` |
| MonitoredPolicy | `monitored_policies` | `apps.monitoring` |
| PolicyVersion | `policy_versions` | `apps.monitoring` |
| PolicyChange | `policy_changes` | `apps.monitoring` |
| Notification | `notifications` | `apps.alerts` |

**To generate migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Member 3's responsibilities:** Review the generated schema, add any indexes or constraints not covered by Django, and coordinate on data types if needed.

---

## 3. Django Backend ↔ NLP Service (Member 2 ↔ Member 4)

**Client file:** `integrations/nlp_client.py`

**Mode A: Backend calls NLP (async via Celery)**
```
Backend → POST {NLP_SERVICE_URL}/analyze/
Headers: X-Internal-Token: <token>
Body:
{
    "document_id": int,
    "document_url": str | null,
    "file_path": str | null
}
```

**Mode B: NLP calls Backend (push model)**
```
NLP Service → POST http://localhost:8000/api/internal/nlp-callback/
Headers: X-Internal-Token: <token>
Body:
{
    "document_id": int,
    "total_clauses": int,
    "clauses": [
        {
            "clause_title": str,
            "original_text": str,
            "category": "data_sharing" | "data_collection" | "data_retention" |
                        "arbitration" | "liability" | "unilateral_change" |
                        "auto_renewal" | "content_license" | "account_termination" |
                        "children_age" | "other",
            "severity": float,  // 0.0 – 1.0
            "simple_explanation": str
        }
    ]
}
```

**Error handling:**
- If NLP service is down: document stays in `processing` status, Celery retries 3× with 30s delay.
- After 3 retries: document marked `failed`, `AnalysisResult.analysis_status = "failed"`.

**Mock mode:** Set `USE_MOCK_NLP=True` in `.env`. Mock returns 3 synthetic clauses.

**Timeout:** 30 seconds per request.

---

## 4. Django Backend ↔ Personalization Service (Member 2 ↔ Member 5)

**Client file:** `integrations/personalization_client.py`

**Backend calls Personalization:**
```
POST {PERSONALIZATION_SERVICE_URL}/score/
Headers: X-Internal-Token: <token>
Body:
{
    "user_id": int,
    "age_group": "under_13" | "13_17" | "18_64" | "65_plus",
    "intended_use": ["student", "personal"],  // array
    "jurisdiction": "india" | "eu" | "usa" | "other",
    "clauses": [
        {
            "clause_id": int,
            "category": str,
            "severity": float,
            "original_text": str
        }
    ]
}

Expected response:
{
    "user_id": int,
    "results": [
        {
            "clause_id": int,
            "relevance_score": float,  // R(c,u) formula result
            "risk_level": "High" | "Medium" | "Low",
            "why_it_matters": str
        }
    ]
}
```

**Scoring formula (from research paper):**
```
R(c,u) = S(c) [λ · max(0, cos(ec, eu)) + (1-λ) · L(c, ju, bu)]
```
- `S(c)` = clause severity (provided by backend)
- `λ` = tunable weight (Member 5 to decide)
- `ec`, `eu` = clause and user embeddings (Member 5 to implement)
- `L(c, ju, bu)` = legal relevance based on jurisdiction and background

**Error handling:** If service unavailable → returns HTTP 503 to frontend.

**Mock mode:** Set `USE_MOCK_PERSONALIZATION=True`. Uses `R ≈ S(c) × 0.7` as placeholder.

---

## 5. Django Backend ↔ Version Tracking Service (Member 2 ↔ Member 6)

**Client file:** `integrations/version_client.py`

**Mode A: Backend polls Version Service**
```
GET {VERSION_SERVICE_URL}/check/?url=<policy_url>&document_id=<id>
Headers: X-Internal-Token: <token>

Expected response:
{
    "document_id": int,
    "version_number": int,
    "version_text": str,
    "content_hash": str,  // SHA-256 of version_text
    "has_changes": bool,
    "changes": [
        {
            "clause_id": int | null,
            "new_clause_title": str,
            "new_clause_text": str,
            "change_type": "added" | "removed" | "modified" | "unchanged",
            "change_direction": "more_favorable" | "neutral" | "less_favorable" | "unclear",
            "magnitude": float  // 0.0 – 1.0
        }
    ]
}
```

**Mode B: Version Service pushes updates to backend**
```
POST http://localhost:8000/api/internal/version-update/
Headers: X-Internal-Token: <token>
Body: (same as Mode A response)
```

**After version update is received:**
1. Backend saves `PolicyVersion` and `PolicyChange` records.
2. Backend queues `generate_alerts_for_document` Celery task.
3. Alert task computes `A = R × D × M` and creates `Notification` records.

**Alert formula (from research paper):**
```
A(c', u) = R(c', u) × D(c') × M(c')
```
Direction weights D:
- Less Favorable = 1.0
- Unclear = 0.8
- Neutral = 0.3
- More Favorable = 0.1

Alert threshold: configurable via `ALERT_THRESHOLD` env variable (default: 0.5).

**Mock mode:** Set `USE_MOCK_VERSION=True`. Returns no changes.

---

## 6. Internal Security

All internal endpoints (`/api/internal/`) require:
```
X-Internal-Token: <INTERNAL_SERVICE_TOKEN>
```

The token is configured in `.env`. All microservices must use the same token value.

---

## 7. Environment Variables Summary

| Variable | Used by | Description |
|----------|---------|-------------|
| `NLP_SERVICE_URL` | Member 4 | URL of NLP microservice |
| `PERSONALIZATION_SERVICE_URL` | Member 5 | URL of personalization service |
| `VERSION_SERVICE_URL` | Member 6 | URL of version tracking service |
| `INTERNAL_SERVICE_TOKEN` | Members 4,5,6 | Shared secret for internal auth |
| `USE_MOCK_NLP` | Member 2 | Use mock NLP (default: True) |
| `USE_MOCK_PERSONALIZATION` | Member 2 | Use mock personalization (default: True) |
| `USE_MOCK_VERSION` | Member 2 | Use mock version tracker (default: True) |
| `ALERT_THRESHOLD` | Member 6 | Min alert score threshold (default: 0.5) |
| `FRONTEND_URL` | Member 1 | CORS origin for React dev server |

---

## 8. Redis / Celery Task Queue

Background tasks run via Celery + Redis.

| Task | Trigger | Description |
|------|---------|-------------|
| `analysis.process_document_nlp` | Document upload | Calls NLP service |
| `alerts.generate_alerts_for_document` | Version update received | Computes alert scores, creates notifications |

Celery worker must be running: `celery -A config worker --loglevel=info`

---

## 9. Development Workflow

For independent development without all services running:

1. Set `USE_MOCK_NLP=True`, `USE_MOCK_PERSONALIZATION=True`, `USE_MOCK_VERSION=True` in `.env`.
2. Each mock returns clearly labelled `[MOCK]` data.
3. As each member's service comes online, change the corresponding `USE_MOCK_*=False`.
4. The internal callback endpoints (`/api/internal/nlp-callback/`, `/api/internal/version-update/`) can be tested with curl:

```bash
curl -X POST http://localhost:8000/api/internal/nlp-callback/ \
  -H "X-Internal-Token: dev-internal-token" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "total_clauses": 1,
    "clauses": [{
      "clause_title": "Test Clause",
      "original_text": "We share your data.",
      "category": "data_sharing",
      "severity": 0.9,
      "simple_explanation": "Your data is shared."
    }]
  }'
```
