# ClauseLens API & Django ORM Database Mapping

**Target Backend:** Django REST Framework (Member 2)  
**Database Engine:** `django.db.backends.postgresql` (`clauselens_db`)

---

## 1. Coordination & Migration Governance Rules

1. **Authoritative Migration Owner:** Member 2 owns Django models and `python manage.py makemigrations` / `migrate` for the production database.
2. **No Conflicting Manual DDL:** Do NOT apply ad-hoc `ALTER TABLE` statements directly to a Django-managed database without updating Django models and generating a corresponding migration.
3. **Role of `ClauseLens/database/`:** The SQL scripts in `database/schema/` serve as the **master relational specification**, local standalone PostgreSQL bootstrap, pgAdmin 4 inspection baseline, and SQL constraint/query test suite.
4. **Recommended Django `Meta` Practice:** Every Django model MUST declare `db_table = '<table_name>'` matching this specification so ORM queries, raw SQL reports, and pgAdmin 4 views stay 100% aligned.

---

## 2. Django Model-to-Table Mapping

| Django App | Django Model | PostgreSQL Table | Primary Key |
|---|---|---|---|
| `accounts` | `User` (`AbstractBaseUser`, `PermissionsMixin`) | `users` | `BigAutoField` (`id`) |
| `accounts` | `AgeGroup` | `age_groups` | `BigAutoField` (`id`) |
| `accounts` | `Jurisdiction` | `jurisdictions` | `BigAutoField` (`id`) |
| `accounts` | `IntendedUseCategory` | `intended_use_categories` | `BigAutoField` (`id`) |
| `accounts` | `UserProfile` | `user_profiles` | `BigAutoField` (`id`) |
| `accounts` | `UserProfileIntendedUse` | `user_profile_intended_uses` | `BigAutoField` (`id`) |
| `documents` | `Document` | `documents` | `BigAutoField` (`id`) |
| `clauses` | `ClauseCategory` | `clause_categories` | `BigAutoField` (`id`) |
| `clauses` | `Clause` | `clauses` | `BigAutoField` (`id`) |
| `clauses` | `ClauseSummary` | `clause_summaries` | `BigAutoField` (`id`) |
| `analysis` | `AnalysisResult` | `analysis_results` | `BigAutoField` (`id`) |
| `risks` | `PersonalizedRisk` | `personalized_risks` | `BigAutoField` (`id`) |
| `versions` | `PolicyVersion` | `policy_versions` | `BigAutoField` (`id`) |
| `versions` | `PolicyChange` | `policy_changes` | `BigAutoField` (`id`) |
| `notifications` | `Notification` | `notifications` | `BigAutoField` (`id`) |
| `monitoring` | `MonitoredPolicy` | `monitored_policies` | `BigAutoField` (`id`) |

---

## 3. Detailed Field, Type & Constraint Mapping

### 3.1 `accounts.User` → `users`
- `AUTH_USER_MODEL = 'accounts.User'`
- `USERNAME_FIELD = 'email'` (or `'username'`; both have `UNIQUE` indexes)
- `REQUIRED_FIELDS = ['username', 'full_name']`
- Fields:
  - `id`: `BigAutoField(primary_key=True)`
  - `username`: `CharField(max_length=150, unique=True)`
  - `full_name`: `CharField(max_length=255)`
  - `email`: `EmailField(max_length=254, unique=True, db_index=True)`
  - `password`: `CharField(max_length=128)` (Django `make_password` / `check_password`)
  - `is_active`: `BooleanField(default=True)`
  - `is_staff`: `BooleanField(default=False)`
  - `is_superuser`: `BooleanField(default=False)`
  - `last_login`: `DateTimeField(null=True, blank=True)`
  - `date_joined`: `DateTimeField(auto_now_add=True)`
  - `updated_at`: `DateTimeField(auto_now=True)`

### 3.2 `accounts.UserProfile` & Lookups → `user_profiles`, `user_profile_intended_uses`
- `UserProfile`:
  - `user`: `OneToOneField(User, on_delete=models.CASCADE, related_name='profile')`
  - `age_group`: `ForeignKey(AgeGroup, on_delete=models.PROTECT)`
  - `jurisdiction`: `ForeignKey(Jurisdiction, on_delete=models.PROTECT)`
  - `intended_uses`: `ManyToManyField(IntendedUseCategory, through='UserProfileIntendedUse')`
- `UserProfileIntendedUse`:
  - `user_profile`: `ForeignKey(UserProfile, on_delete=models.CASCADE)`
  - `intended_use`: `ForeignKey(IntendedUseCategory, on_delete=models.PROTECT)`
  - `UniqueConstraint(fields=['user_profile', 'intended_use'], name='uq_profile_intended_use')`

### 3.3 `documents.Document` → `documents`
- `user`: `ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)`
- `document_name`: `CharField(max_length=255)`
- `document_type`: `CharField(max_length=50, choices=[('Terms and Conditions', ...), ('Privacy Policy', ...), ('Other Legal Document', ...)])`
- `file_path`: `CharField(max_length=500, null=True, blank=True)` (or `FileField` mapping path)
- `policy_url`: `URLField(max_length=2048, null=True, blank=True)`
- `source_type`: `CharField(max_length=30, choices=[('PDF Upload', ...), ('URL', ...), ('Manual Text', ...)])`
- `processing_status`: `CharField(max_length=30, default='Uploaded')`
- `is_public_policy`: `BooleanField(default=False)`
- `is_deleted`: `BooleanField(default=False)`
- `deleted_at`: `DateTimeField(null=True, blank=True)`
- `created_at`: `DateTimeField(auto_now_add=True, db_index=True)`
- `updated_at`: `DateTimeField(auto_now=True)`

### 3.4 `clauses.Clause` & `clauses.ClauseSummary` → `clauses`, `clause_summaries`
- `Clause`:
  - `document`: `ForeignKey(Document, on_delete=models.PROTECT, related_name='clauses')`
  - `category`: `ForeignKey(ClauseCategory, on_delete=models.PROTECT)`
  - `clause_title`: `CharField(max_length=255)`
  - `original_text`: `TextField()`
  - `severity_score`: `DecimalField(max_digits=4, decimal_places=3)` (`0.000` to `1.000`)
  - `clause_order`: `PositiveIntegerField()`
  - `UniqueConstraint(fields=['document', 'clause_order'], name='uq_clauses_doc_order')`
- `ClauseSummary`:
  - `clause`: `ForeignKey(Clause, on_delete=models.CASCADE, related_name='summaries')`
  - `simple_explanation`: `TextField()`
  - `summary_language`: `CharField(max_length=20, default='en')`
  - `model_name`: `CharField(max_length=100)`
  - `summary_version`: `PositiveIntegerField(default=1)`

### 3.5 `analysis.AnalysisResult` → `analysis_results`
- `document`: `ForeignKey(Document, on_delete=models.PROTECT, related_name='analyses')`
- `total_clauses`, `high_risk_count`, `medium_risk_count`, `low_risk_count`: `PositiveIntegerField(default=0)`
- `overall_risk_score`: `DecimalField(max_digits=5, decimal_places=2, default=0.00)` (`0.00` to `100.00`)
- `analysis_status`: `CharField(max_length=30, default='Pending')`

### 3.6 `risks.PersonalizedRisk` → `personalized_risks`
- `user`: `ForeignKey(User, on_delete=models.CASCADE)`
- `clause`: `ForeignKey(Clause, on_delete=models.CASCADE)`
- `relevance_score`: `DecimalField(max_digits=4, decimal_places=3)` (`0.000` to `1.000`)
- `risk_level`: `CharField(max_length=20, choices=[('Low', ...), ('Medium', ...), ('High', ...), ('Critical', ...)])`
- `why_it_matters`: `TextField()`
- `UniqueConstraint(fields=['user', 'clause'], name='uq_personalized_risks_user_clause')`

### 3.7 `versions.PolicyVersion` & `versions.PolicyChange` → `policy_versions`, `policy_changes`
- `PolicyVersion`:
  - `document`: `ForeignKey(Document, on_delete=models.PROTECT, related_name='versions')`
  - `version_number`: `CharField(max_length=30)`
  - `version_sequence`: `PositiveIntegerField()`
  - `version_text`: `TextField(null=True, blank=True)`
  - `stored_reference`: `CharField(max_length=500, null=True, blank=True)`
  - `content_hash`: `CharField(max_length=64)` (SHA-256 hex)
  - `UniqueConstraint(fields=['document', 'content_hash'], name='uq_policy_versions_doc_hash')`
- `PolicyChange`:
  - `document`: `ForeignKey(Document, on_delete=models.PROTECT)`
  - `old_version`: `ForeignKey(PolicyVersion, on_delete=models.PROTECT, related_name='changes_from')`
  - `new_version`: `ForeignKey(PolicyVersion, on_delete=models.PROTECT, related_name='changes_to')`
  - `old_clause`: `ForeignKey(Clause, null=True, blank=True, on_delete=models.SET_NULL, related_name='removed_or_old_changes')`
  - `new_clause`: `ForeignKey(Clause, null=True, blank=True, on_delete=models.SET_NULL, related_name='added_or_new_changes')`
  - `change_type`: `CharField(max_length=20)` (`Added`, `Removed`, `Modified`, `Unchanged`)
  - `change_direction`: `CharField(max_length=20)` (`More Favorable`, `Neutral`, `Less Favorable`, `Unclear`)
  - `magnitude`: `DecimalField(max_digits=4, decimal_places=3)` (`0.000` to `1.000`)

### 3.8 `notifications.Notification` & `monitoring.MonitoredPolicy`
- `Notification`:
  - `user`: `ForeignKey(User, on_delete=models.CASCADE)`
  - `policy_change`: `ForeignKey(PolicyChange, null=True, blank=True, on_delete=models.SET_NULL)`
  - `alert_score`: `DecimalField(max_digits=4, decimal_places=3, default=0.000)`
  - `severity`: `CharField(max_length=20, default='Info')`
  - `is_read`: `BooleanField(default=False, db_index=True)`
  - `UniqueConstraint(fields=['user', 'policy_change'], condition=Q(policy_change__isnull=False), name='uq_notifications_user_policy_change')`
- `MonitoredPolicy`:
  - `user`: `ForeignKey(User, on_delete=models.CASCADE)`
  - `document`: `ForeignKey(Document, on_delete=models.PROTECT)`
  - `policy_url`: `URLField(max_length=2048)`
  - `monitoring_status`: `CharField(max_length=20, default='Active')`
  - `check_interval_hours`: `PositiveIntegerField(default=24)`
  - `UniqueConstraint(fields=['user', 'document'], name='uq_monitored_policies_user_doc')`

---

## 4. API Endpoint → Query Mapping

| DRF Endpoint | Primary Tables | Reference SQL |
|---|---|---|
| `GET /api/v1/dashboard/` | `users`, `user_profiles`, `documents`, `analysis_results`, `monitored_policies`, `notifications`, `policy_changes` | [dashboard_queries.sql](file:///C:/Users/User/.gemini/antigravity/scratch/ClauseLens/database/queries/dashboard_queries.sql) |
| `GET /api/v1/documents/` | `documents`, `analysis_results` | [document_queries.sql](file:///C:/Users/User/.gemini/antigravity/scratch/ClauseLens/database/queries/document_queries.sql) |
| `GET /api/v1/documents/{id}/clauses/` | `clauses`, `clause_categories`, `clause_summaries` | [clause_queries.sql](file:///C:/Users/User/.gemini/antigravity/scratch/ClauseLens/database/queries/clause_queries.sql) |
| `GET /api/v1/risks/personalized/` | `personalized_risks`, `clauses`, `user_profiles`, `age_groups`, `jurisdictions` | [risk_queries.sql](file:///C:/Users/User/.gemini/antigravity/scratch/ClauseLens/database/queries/risk_queries.sql) |
| `GET /api/v1/monitoring/` & `/versions/` | `monitored_policies`, `policy_versions`, `policy_changes` | [version_queries.sql](file:///C:/Users/User/.gemini/antigravity/scratch/ClauseLens/database/queries/version_queries.sql) |
| `GET /api/v1/notifications/` | `notifications`, `policy_changes`, `documents` | [notification_queries.sql](file:///C:/Users/User/.gemini/antigravity/scratch/ClauseLens/database/queries/notification_queries.sql) |
