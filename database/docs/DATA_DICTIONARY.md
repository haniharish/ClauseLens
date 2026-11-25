# ClauseLens Data Dictionary

**Database Name:** `clauselens_db`  
**DBMS:** PostgreSQL 15+  
**Total Tables:** 16 (11 core operational tables + 5 normalized lookup/junction tables)

---

## 1. `users`
- **Purpose:** Authoritative user account and authentication table managed by Django (`AbstractBaseUser` + `PermissionsMixin` compatible).

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_users` |
| `username` | `VARCHAR(150)` | — | — | NOT NULL | — | `uq_users_username`, `CHAR_LENGTH(TRIM(username)) >= 3` |
| `full_name` | `VARCHAR(255)` | — | — | NOT NULL | — | `CHAR_LENGTH(TRIM(full_name)) >= 1` |
| `email` | `VARCHAR(254)` | — | — | NOT NULL | — | `uq_users_email`, regex email validation |
| `password` | `VARCHAR(128)` | — | — | NOT NULL | — | `CHAR_LENGTH(password) >= 20` (hashed only) |
| `is_active` | `BOOLEAN` | — | — | NOT NULL | `TRUE` | — |
| `is_staff` | `BOOLEAN` | — | — | NOT NULL | `FALSE` | Django Admin compatibility |
| `is_superuser` | `BOOLEAN` | — | — | NOT NULL | `FALSE` | Django Permissions compatibility |
| `last_login` | `TIMESTAMPTZ` | — | — | NULL | `NULL` | — |
| `date_joined` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | — |
| `updated_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | Auto-updated via trigger |

---

## 2. `age_groups` (Lookup)
- **Purpose:** Canonical age-group brackets for regulatory and youth-safety risk weighting.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_age_groups` |
| `code` | `VARCHAR(32)` | — | — | NOT NULL | — | `uq_age_groups_code` (`under_13`, `13_17`, `18_64`, `65_plus`) |
| `label` | `VARCHAR(50)` | — | — | NOT NULL | — | `uq_age_groups_label` (`Under 13`, `13-17`, `18-64`, `65+`) |
| `min_age` | `SMALLINT` | — | — | NOT NULL | — | `min_age >= 0` |
| `max_age` | `SMALLINT` | — | — | NULL | `NULL` | `max_age IS NULL OR max_age >= min_age` |
| `description` | `TEXT` | — | — | NOT NULL | `''` | — |

---

## 3. `jurisdictions` (Lookup)
- **Purpose:** Legal jurisdictions governing user privacy and consumer protection rights.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_jurisdictions` |
| `code` | `VARCHAR(32)` | — | — | NOT NULL | — | `uq_jurisdictions_code` (`IN`, `EU`, `US`, `OTHER`) |
| `name` | `VARCHAR(100)` | — | — | NOT NULL | — | `uq_jurisdictions_name` (`India`, `European Union`, `United States`, `Other`) |
| `primary_framework` | `VARCHAR(150)` | — | — | NOT NULL | `''` | — |
| `description` | `TEXT` | — | — | NOT NULL | `''` | — |

---

## 4. `intended_use_categories` (Lookup)
- **Purpose:** Reusable intended-use tags describing how a user interacts with a service.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_intended_use_categories` |
| `code` | `VARCHAR(32)` | — | — | NOT NULL | — | `uq_intended_use_code` (`personal`, `student`, `freelancer`, `business`, `parent_of_minor`) |
| `name` | `VARCHAR(100)` | — | — | NOT NULL | — | `uq_intended_use_name` |
| `description` | `TEXT` | — | — | NOT NULL | `''` | — |

---

## 5. `user_profiles`
- **Purpose:** Stores each user's 1:1 personalization context (`age_group`, `jurisdiction`).

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_user_profiles` |
| `user_id` | `BIGINT` | — | `users(id)` | NOT NULL | — | `uq_user_profiles_user_id` (1:1), `ON DELETE CASCADE` |
| `age_group_id` | `BIGINT` | — | `age_groups(id)` | NOT NULL | — | `ON DELETE RESTRICT` |
| `jurisdiction_id` | `BIGINT` | — | `jurisdictions(id)` | NOT NULL | — | `ON DELETE RESTRICT` |
| `created_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | — |
| `updated_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | Auto-updated via trigger |

---

## 6. `user_profile_intended_uses` (Junction)
- **Purpose:** Normalized many-to-many mapping allowing multiple intended-use tags per user profile.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_user_profile_intended_uses` |
| `user_profile_id` | `BIGINT` | — | `user_profiles(id)` | NOT NULL | — | `ON DELETE CASCADE` |
| `intended_use_id` | `BIGINT` | — | `intended_use_categories(id)` | NOT NULL | — | `ON DELETE RESTRICT` |
| `created_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | `uq_profile_intended_use` on `(user_profile_id, intended_use_id)` |

---

## 7. `documents`
- **Purpose:** Stores uploaded PDF file references, policy URLs, ownership, and processing state.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_documents` |
| `user_id` | `BIGINT` | — | `users(id)` | NULL | `NULL` | `ON DELETE SET NULL` (preserves shared policy history) |
| `document_name` | `VARCHAR(255)` | — | — | NOT NULL | — | `CHAR_LENGTH(TRIM(document_name)) >= 1` |
| `document_type` | `VARCHAR(50)` | — | — | NOT NULL | — | `IN ('Terms and Conditions', 'Privacy Policy', 'Other Legal Document')` |
| `file_path` | `VARCHAR(500)` | — | — | NULL | `NULL` | Required when `source_type = 'PDF Upload'` |
| `policy_url` | `VARCHAR(2048)` | — | — | NULL | `NULL` | Required when `source_type = 'URL'`; `http(s)://` check |
| `source_type` | `VARCHAR(30)` | — | — | NOT NULL | — | `IN ('PDF Upload', 'URL', 'Manual Text')` |
| `processing_status` | `VARCHAR(30)` | — | — | NOT NULL | `'Uploaded'` | `IN ('Uploaded', 'Pending', 'Processing', 'Completed', 'Failed')` |
| `is_public_policy` | `BOOLEAN` | — | — | NOT NULL | `FALSE` | Enables multi-user shared monitoring |
| `is_deleted` | `BOOLEAN` | — | — | NOT NULL | `FALSE` | Soft-delete consistency check with `deleted_at` |
| `deleted_at` | `TIMESTAMPTZ` | — | — | NULL | `NULL` | Must be non-null iff `is_deleted = TRUE` |
| `created_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | — |
| `updated_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | Auto-updated via trigger |

---

## 8. `clause_categories` (Lookup)
- **Purpose:** Canonical taxonomy of the 11 ClauseLens legal clause categories.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_clause_categories` |
| `code` | `VARCHAR(50)` | — | — | NOT NULL | — | `uq_clause_categories_code` |
| `name` | `VARCHAR(100)` | — | — | NOT NULL | — | `uq_clause_categories_name` |
| `default_weight` | `NUMERIC(4,3)` | — | — | NOT NULL | `0.500` | `0.000 <= default_weight <= 1.000` |
| `description` | `TEXT` | — | — | NOT NULL | `''` | — |

---

## 9. `clauses`
- **Purpose:** Stores individual legal clauses extracted from documents, preserving original legal text.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_clauses` |
| `document_id` | `BIGINT` | — | `documents(id)` | NOT NULL | — | `ON DELETE RESTRICT` |
| `category_id` | `BIGINT` | — | `clause_categories(id)` | NOT NULL | — | `ON DELETE RESTRICT` |
| `clause_title` | `VARCHAR(255)` | — | — | NOT NULL | — | Non-empty trimmed string |
| `original_text` | `TEXT` | — | — | NOT NULL | — | Non-empty trimmed string |
| `severity_score` | `NUMERIC(4,3)` | — | — | NOT NULL | — | `0.000 <= severity_score <= 1.000` |
| `clause_order` | `INTEGER` | — | — | NOT NULL | — | `clause_order >= 1`, `uq_clauses_doc_order` on `(document_id, clause_order)` |
| `created_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | — |

---

## 10. `clause_summaries`
- **Purpose:** Stores AI-generated plain-language summaries separately from `clauses.original_text`.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_clause_summaries` |
| `clause_id` | `BIGINT` | — | `clauses(id)` | NOT NULL | — | `ON DELETE CASCADE` |
| `simple_explanation` | `TEXT` | — | — | NOT NULL | — | Non-empty trimmed string |
| `summary_language` | `VARCHAR(20)` | — | — | NOT NULL | `'en'` | — |
| `model_name` | `VARCHAR(100)` | — | — | NOT NULL | — | Non-empty trimmed string |
| `summary_version` | `INTEGER` | — | — | NOT NULL | `1` | `summary_version >= 1`, `uq_clause_summaries_version` on `(clause_id, summary_language, model_name, summary_version)` |
| `created_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | — |

---

## 11. `analysis_results`
- **Purpose:** Stores aggregate document-level risk scores and clause risk distributions over time.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_analysis_results` |
| `document_id` | `BIGINT` | — | `documents(id)` | NOT NULL | — | `ON DELETE RESTRICT` |
| `total_clauses` | `INTEGER` | — | — | NOT NULL | `0` | `>= 0` |
| `high_risk_count` | `INTEGER` | — | — | NOT NULL | `0` | `>= 0` |
| `medium_risk_count` | `INTEGER` | — | — | NOT NULL | `0` | `>= 0` |
| `low_risk_count` | `INTEGER` | — | — | NOT NULL | `0` | `>= 0`, `high + medium + low <= total_clauses` |
| `overall_risk_score` | `NUMERIC(5,2)` | — | — | NOT NULL | `0.00` | `0.00 <= overall_risk_score <= 100.00` |
| `analysis_status` | `VARCHAR(30)` | — | — | NOT NULL | `'Pending'` | `IN ('Pending', 'Processing', 'Completed', 'Failed')` |
| `created_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | — |

---

## 12. `personalized_risks`
- **Purpose:** Stores context-aware clause relevance scores and personalized explanations per user.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_personalized_risks` |
| `user_id` | `BIGINT` | — | `users(id)` | NOT NULL | — | `ON DELETE CASCADE` |
| `clause_id` | `BIGINT` | — | `clauses(id)` | NOT NULL | — | `ON DELETE CASCADE`, `uq_personalized_risks_user_clause` on `(user_id, clause_id)` |
| `relevance_score` | `NUMERIC(4,3)` | — | — | NOT NULL | — | `0.000 <= relevance_score <= 1.000` |
| `risk_level` | `VARCHAR(20)` | — | — | NOT NULL | — | `IN ('Low', 'Medium', 'High', 'Critical')` |
| `why_it_matters` | `TEXT` | — | — | NOT NULL | — | Non-empty trimmed string |
| `created_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | — |

---

## 13. `policy_versions`
- **Purpose:** Immutable policy version snapshots with SHA-256 content hashes for change detection.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_policy_versions` |
| `document_id` | `BIGINT` | — | `documents(id)` | NOT NULL | — | `ON DELETE RESTRICT` |
| `version_number` | `VARCHAR(30)` | — | — | NOT NULL | — | `uq_policy_versions_doc_number` on `(document_id, version_number)` |
| `version_sequence` | `INTEGER` | — | — | NOT NULL | — | `>= 1`, `uq_policy_versions_doc_seq` on `(document_id, version_sequence)` |
| `version_text` | `TEXT` | — | — | NULL | `NULL` | Either `version_text` or `stored_reference` must be non-null |
| `stored_reference` | `VARCHAR(500)` | — | — | NULL | `NULL` | Object/file reference if text is offloaded |
| `content_hash` | `CHAR(64)` | — | — | NOT NULL | — | 64-char hex SHA-256 regex, `uq_policy_versions_doc_hash` on `(document_id, content_hash)` |
| `fetched_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | — |
| `created_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | — |

---

## 14. `policy_changes`
- **Purpose:** Records clause-level differences between two `policy_versions`.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_policy_changes` |
| `document_id` | `BIGINT` | — | `documents(id)` | NOT NULL | — | `ON DELETE RESTRICT` |
| `old_version_id` | `BIGINT` | — | `policy_versions(id)` | NOT NULL | — | `ON DELETE RESTRICT`, `old_version_id <> new_version_id` |
| `new_version_id` | `BIGINT` | — | `policy_versions(id)` | NOT NULL | — | `ON DELETE RESTRICT` |
| `old_clause_id` | `BIGINT` | — | `clauses(id)` | NULL | `NULL` | `ON DELETE SET NULL`; NULL when `Added` |
| `new_clause_id` | `BIGINT` | — | `clauses(id)` | NULL | `NULL` | `ON DELETE SET NULL`; NULL when `Removed` |
| `change_type` | `VARCHAR(20)` | — | — | NOT NULL | — | `IN ('Added', 'Removed', 'Modified', 'Unchanged')` |
| `change_direction` | `VARCHAR(20)` | — | — | NOT NULL | — | `IN ('More Favorable', 'Neutral', 'Less Favorable', 'Unclear')` |
| `magnitude` | `NUMERIC(4,3)` | — | — | NOT NULL | — | `0.000 <= magnitude <= 1.000` |
| `change_summary` | `TEXT` | — | — | NULL | `NULL` | — |
| `detected_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | — |

---

## 15. `notifications`
- **Purpose:** Personalized alerts delivered to users when policy changes or risks occur.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_notifications` |
| `user_id` | `BIGINT` | — | `users(id)` | NOT NULL | — | `ON DELETE CASCADE` |
| `policy_change_id` | `BIGINT` | — | `policy_changes(id)` | NULL | `NULL` | `ON DELETE SET NULL`; partial unique index `(user_id, policy_change_id) WHERE policy_change_id IS NOT NULL` |
| `title` | `VARCHAR(255)` | — | — | NOT NULL | — | Non-empty trimmed string |
| `message` | `TEXT` | — | — | NOT NULL | — | Non-empty trimmed string |
| `alert_score` | `NUMERIC(4,3)` | — | — | NOT NULL | `0.000` | `0.000 <= alert_score <= 1.000` |
| `severity` | `VARCHAR(20)` | — | — | NOT NULL | `'Info'` | `IN ('Info', 'Low', 'Medium', 'High', 'Critical')` |
| `is_read` | `BOOLEAN` | — | — | NOT NULL | `FALSE` | — |
| `created_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | — |

---

## 16. `monitored_policies`
- **Purpose:** Tracks user monitoring subscriptions and polling schedules for public policy URLs.

| Column | Data Type | PK | FK | Nullable | Default | Constraints |
|---|---|---|---|---|---|---|
| `id` | `BIGINT` | Yes | — | NOT NULL | `IDENTITY` | `pk_monitored_policies` |
| `user_id` | `BIGINT` | — | `users(id)` | NOT NULL | — | `ON DELETE CASCADE` |
| `document_id` | `BIGINT` | — | `documents(id)` | NOT NULL | — | `ON DELETE RESTRICT`, `uq_monitored_policies_user_doc` on `(user_id, document_id)` |
| `policy_url` | `VARCHAR(2048)` | — | — | NOT NULL | — | `http(s)://` regex check |
| `monitoring_status` | `VARCHAR(20)` | — | — | NOT NULL | `'Active'` | `IN ('Active', 'Paused', 'Failed')` |
| `check_interval_hours` | `INTEGER` | — | — | NOT NULL | `24` | `check_interval_hours >= 1` |
| `last_checked_at` | `TIMESTAMPTZ` | — | — | NULL | `NULL` | `next_check_at >= last_checked_at` (when both set) |
| `next_check_at` | `TIMESTAMPTZ` | — | — | NULL | `NULL` | — |
| `created_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | — |
| `updated_at` | `TIMESTAMPTZ` | — | — | NOT NULL | `CURRENT_TIMESTAMP` | Auto-updated via trigger |
