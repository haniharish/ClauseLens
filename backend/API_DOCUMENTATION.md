# ClauseLens API Documentation

Base URL: `http://localhost:8000/api/`

All responses follow the standard envelope:

```json
// Success
{ "success": true, "message": "...", "data": {} }

// Error
{ "success": false, "message": "...", "errors": {} }
```

Authentication: `Authorization: Bearer <access_token>`

---

## 1. Authentication (`/api/auth/`)

### POST `/api/auth/register/`
Register a new user account.

**Request body:**
```json
{
  "username": "johndoe",
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "StrongPass1234!",
  "password_confirm": "StrongPass1234!"
}
```

**Response 201:**
```json
{
  "success": true,
  "message": "Account created successfully.",
  "data": {
    "user": { "id": 1, "username": "johndoe", "email": "john@example.com", ... },
    "access": "<jwt_access_token>",
    "refresh": "<jwt_refresh_token>"
  }
}
```

---

### POST `/api/auth/login/`
Login and obtain JWT tokens.

**Request body:**
```json
{ "email": "john@example.com", "password": "StrongPass1234!" }
```

**Response 200:**
```json
{ "success": true, "data": { "access": "...", "refresh": "..." } }
```

---

### POST `/api/auth/token/refresh/`
Refresh an expired access token.

**Request body:**
```json
{ "refresh": "<refresh_token>" }
```

---

### POST `/api/auth/logout/`
🔒 Authenticated. Blacklist the refresh token.

**Request body:**
```json
{ "refresh": "<refresh_token>" }
```

---

### GET `/api/auth/me/`
🔒 Authenticated. Return the logged-in user's details.

**Response 200:**
```json
{
  "success": true,
  "data": { "id": 1, "username": "johndoe", "email": "john@example.com", "full_name": "John Doe", "date_joined": "..." }
}
```

---

### POST `/api/auth/change-password/`
🔒 Authenticated. Change the user's password.

**Request body:**
```json
{
  "old_password": "OldPass1234!",
  "new_password": "NewPass5678!",
  "new_password_confirm": "NewPass5678!"
}
```

---

## 2. User Profile (`/api/profile/`)

All endpoints require authentication.

### GET `/api/profile/`
Retrieve the current user's profile.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "age_group": "18_64",
    "intended_use": ["student", "personal"],
    "jurisdiction": "india",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

### POST `/api/profile/`
Create a new profile.

**Request body:**
```json
{
  "age_group": "18_64",
  "intended_use": ["student"],
  "jurisdiction": "india"
}
```

Valid `age_group` values: `under_13`, `13_17`, `18_64`, `65_plus`
Valid `intended_use` values: `personal`, `student`, `freelancer`, `business`, `parent_of_minor`
Valid `jurisdiction` values: `india`, `eu`, `usa`, `other`

### PUT `/api/profile/`
Full update. Same body as POST.

### PATCH `/api/profile/`
Partial update. Any subset of POST fields.

### DELETE `/api/profile/`
Delete the profile.

---

## 3. Documents (`/api/documents/`)

### POST `/api/documents/upload/`
Upload a PDF document.

**Content-Type:** `multipart/form-data`

**Form fields:**
- `file` (required): PDF file, max 10 MB
- `document_name` (optional): Display name

**Response 201:**
```json
{
  "success": true,
  "message": "Document uploaded successfully. Processing has begun.",
  "data": {
    "id": 1,
    "document_name": "My Policy",
    "document_type": "pdf",
    "file_url": "http://localhost:8000/media/documents/1/policy.pdf",
    "policy_url": null,
    "status": "processing",
    "uploaded_at": "...",
    "updated_at": "..."
  }
}
```

---

### POST `/api/documents/url/`
Submit a policy URL for analysis.

**Request body:**
```json
{
  "policy_url": "https://example.com/privacy-policy",
  "document_name": "Example Privacy Policy"
}
```

**Response 201:** Same shape as upload.

---

### GET `/api/documents/`
List all documents belonging to the authenticated user (paginated).

**Query params:** `page`, `page_size`

---

### GET `/api/documents/{id}/`
Retrieve a specific document.

---

### DELETE `/api/documents/{id}/`
Delete a document and all its related data.

---

### GET `/api/documents/{id}/status/`
Check document processing status.

**Response:**
```json
{ "success": true, "data": { "id": 1, "status": "completed", "updated_at": "..." } }
```

Possible statuses: `uploaded`, `processing`, `completed`, `failed`

---

## 4. Analysis (`/api/analysis/`)

### GET `/api/analysis/documents/{id}/clauses/`
List all extracted clauses for a document (paginated, ordered by severity).

**Response data items:**
```json
{
  "id": 10,
  "document": 1,
  "clause_title": "Third Party Data Sharing",
  "original_text": "The company may share...",
  "category": "data_sharing",
  "severity": 0.85,
  "simple_explanation": "Your data may be shared.",
  "created_at": "..."
}
```

### GET `/api/analysis/documents/{id}/result/`
Get the aggregate analysis result.

```json
{
  "id": 1,
  "document": 1,
  "total_clauses": 25,
  "high_risk_count": 8,
  "medium_risk_count": 12,
  "low_risk_count": 5,
  "overall_risk_score": 0.72,
  "analysis_status": "completed",
  "created_at": "..."
}
```

---

## 5. Personalization (`/api/personalization/`)

### GET `/api/personalization/documents/{id}/risks/`
Get personalised risk scores for all clauses in a document.
If not calculated yet, triggers the personalization service.

**Response data items:**
```json
{
  "id": 1,
  "clause": 10,
  "clause_title": "Third Party Data Sharing",
  "relevance_score": 0.85,
  "risk_level": "High",
  "why_it_matters": "This clause is relevant because you are a student in India.",
  "created_at": "..."
}
```

**503** if personalization service is unavailable.

---

## 6. Policy Monitoring (`/api/monitoring/`)

### POST `/api/monitoring/`
Add a policy URL to monitoring.

```json
{
  "policy_url": "https://google.com/privacy",
  "policy_name": "Google Privacy Policy",
  "check_interval_hours": 24
}
```

### GET `/api/monitoring/`
List all monitored policies (paginated).

### GET `/api/monitoring/{id}/`
Get monitoring details.

### PATCH `/api/monitoring/{id}/`
Update settings (e.g., pause/resume):
```json
{ "monitoring_status": "paused" }
```
Valid `monitoring_status` values: `active`, `paused`

### DELETE `/api/monitoring/{id}/`
Stop monitoring a policy.

---

## 7. Versions & Changes

### GET `/api/versions/`
List all policy versions across user's documents.

### GET `/api/versions/{document_id}/`
List all versions of a specific document.

### GET `/api/versions/{document_id}/compare/`
Compare the last two versions of a document.

**Response:**
```json
{
  "old_version": { "version_number": 1, "content_hash": "...", ... },
  "new_version": { "version_number": 2, "content_hash": "...", ... },
  "changes": [...]
}
```

### GET `/api/changes/{document_id}/`
List all clause-level changes for a document.

---

## 8. Notifications (`/api/notifications/`)

### GET `/api/notifications/`
List notifications (paginated).

**Query params:** `?unread=true` to filter unread only.

### GET `/api/notifications/{id}/`
Retrieve a notification.

### PATCH `/api/notifications/{id}/read/`
Mark a notification as read.

### PATCH `/api/notifications/read-all/`
Mark all notifications as read.

### DELETE `/api/notifications/{id}/`
Delete a notification.

---

## 9. Dashboard (`/api/dashboard/`)

### GET `/api/dashboard/`
Return dashboard statistics calculated from actual database records.

**Response:**
```json
{
  "success": true,
  "data": {
    "documents_analyzed": 24,
    "high_risk_clauses": 18,
    "policies_monitored": 8,
    "changes_detected": 12,
    "risk_distribution": { "high": 8, "medium": 15, "low": 20 },
    "recent_documents": [...],
    "recent_changes": [...],
    "recent_notifications": [...]
  }
}
```

---

## 10. Internal Endpoints (`/api/internal/`)

> These endpoints are **NOT** for the frontend. They are called by other microservices.
> Protected by `X-Internal-Token: <INTERNAL_SERVICE_TOKEN>` header.

### POST `/api/internal/nlp-callback/`
Called by Member 4's NLP module when analysis is complete.

**Request body:**
```json
{
  "document_id": 1,
  "total_clauses": 25,
  "clauses": [
    {
      "clause_title": "Third Party Data Sharing",
      "original_text": "...",
      "category": "data_sharing",
      "severity": 0.85,
      "simple_explanation": "..."
    }
  ]
}
```

### POST `/api/internal/version-update/`
Called by Member 6's version tracking module when changes are detected.

**Request body:**
```json
{
  "document_id": 1,
  "version_number": 2,
  "version_text": "Full policy text...",
  "content_hash": "sha256_hash_string",
  "changes": [
    {
      "clause_id": 10,
      "change_type": "modified",
      "change_direction": "less_favorable",
      "magnitude": 0.75
    }
  ]
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Validation error |
| 401 | Authentication required |
| 403 | Permission denied (not your resource) |
| 404 | Not found |
| 500 | Server error |
| 503 | Dependent service unavailable |

---

## Pagination

All list endpoints return paginated responses:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/documents/?page=2",
  "previous": null,
  "results": [...]
}
```

Default page size: 20. Use `?page_size=50` to change (max 100).

---

## Interactive Docs

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
