# ClauseLens Database Module (`clauselens_db`)

**Module Owner:** Member 3 – Database Design & Management  
**Project:** *ClauseLens: Context-Aware Terms & Conditions Risk Summarization with Version-Diff Personalized Alerts*

---

## 1. What the ClauseLens Database Does

`clauselens_db` is the single relational PostgreSQL source of truth for ClauseLens. It stores and enforces integrity across:
- User accounts and Django-compatible authentication metadata (`users`)
- Normalized personalization profiles (`age_groups`, `jurisdictions`, `intended_use_categories`, `user_profiles`, `user_profile_intended_uses`)
- Uploaded PDF metadata, policy URLs, and NLP pipeline statuses (`documents`)
- Extracted legal clauses, 11 canonical clause categories, and separated AI plain-language summaries (`clause_categories`, `clauses`, `clause_summaries`)
- Document-level risk summaries (`analysis_results`) and user-tailored clause relevance scores (`personalized_risks`)
- Immutable policy snapshots, SHA-256 content hashes, clause-level diffs (`Added`, `Removed`, `Modified`, `Unchanged`), monitoring subscriptions, and deduplicated user alerts (`policy_versions`, `policy_changes`, `monitored_policies`, `notifications`)

---

## 2. Why PostgreSQL Was Selected

1. **ACID Integrity & Retention Safety:** Foreign keys with `RESTRICT` and `SET NULL` prevent accidental cascading loss of legal policy history when users or accounts change.
2. **Rich Constraint Enforcement:** Native `CHECK` constraints validate score ranges (`0.000`–`1.000` and `0.00`–`100.00`), SHA-256 hex format, and diff clause-presence rules at the database layer.
3. **Partial & Composite Indexes:** Speeds up active-document feeds, unread-notification counts, and active monitoring polls without unnecessary index bloat.
4. **First-Class Django ORM Support:** Maps cleanly to Member 2's Django REST Framework backend (`django.db.backends.postgresql`).

---

## 3. How to Install PostgreSQL

### Windows
1. Download the PostgreSQL 15 or 16 installer from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/).
2. Run the installer, choose a data directory, set a secure `postgres` superuser password, and keep default port `5432`.
3. Add `C:\Program Files\PostgreSQL\<version>\bin` to your system `PATH` so `psql` works in PowerShell/Command Prompt.
4. Verify installation:
   ```powershell
   psql --version
   ```

### Linux (Ubuntu/Debian) & macOS
- **Ubuntu/Debian:** `sudo apt update && sudo apt install postgresql postgresql-contrib`
- **macOS (Homebrew):** `brew install postgresql@16 && brew services start postgresql@16`

---

## 4. How to Install pgAdmin 4

1. The Windows PostgreSQL installer includes **pgAdmin 4** by default (check the pgAdmin component during setup), or download it standalone from [pgadmin.org/download](https://www.pgadmin.org/download/).
2. Launch pgAdmin 4, set a master password, and register a server connection:
   - **Host:** `localhost`
   - **Port:** `5432`
   - **Maintenance DB:** `postgres` (or `clauselens_db` after creation)
   - **Username:** `postgres` (for admin setup) or `clauselens_app` (for app runtime)

---

## 5. How to Create the Database

From the `ClauseLens/database` directory:

```bash
psql -U postgres -f scripts/create_database.sql
```

This creates `clauselens_db` (UTF-8) if it does not exist, enables `pgcrypto`, and runs `schema/01_users.sql` through `schema/10_monitoring.sql` in strict dependency order.

Optionally configure least-privilege application roles (supply passwords at runtime—never hardcode):

```bash
psql -U postgres -d clauselens_db \
  -v app_password="YOUR_STRONG_APP_PASSWORD" \
  -v ro_password="YOUR_STRONG_RO_PASSWORD" \
  -f scripts/setup_roles.sql
```

---

## 6. How to Execute SQL Scripts

If running schema files manually in `psql` or pgAdmin 4 Query Tool against `clauselens_db`, execute in this exact order:

1. `schema/01_users.sql`
2. `schema/02_profiles.sql`
3. `schema/03_documents.sql`
4. `schema/04_clauses.sql`
5. `schema/05_analysis_results.sql`
6. `schema/06_personalized_risks.sql`
7. `schema/07_policy_versions.sql`
8. `schema/08_policy_changes.sql`
9. `schema/09_notifications.sql`
10. `schema/10_monitoring.sql`

To reset a local development database cleanly:
```bash
psql -U postgres -d clauselens_db -f scripts/reset_database.sql
```

---

## 7. How to Connect to the Database

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Update `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` in `.env` (never commit `.env`).
3. Connect via `psql`:
   ```bash
   psql -h localhost -p 5432 -U clauselens_app -d clauselens_db
   ```

---

## 8. How to Insert Demonstration Data

All demonstration records are **illustrative/fictional academic samples** (Alex in India, Sarah in USA, John in EU, and 4 demo policies). Load them in order:

```bash
psql -U postgres -d clauselens_db -v ON_ERROR_STOP=1 -f seed/sample_users.sql
psql -U postgres -d clauselens_db -v ON_ERROR_STOP=1 -f seed/sample_documents.sql
psql -U postgres -d clauselens_db -v ON_ERROR_STOP=1 -f seed/sample_clauses.sql
psql -U postgres -d clauselens_db -v ON_ERROR_STOP=1 -f seed/sample_versions.sql
```

---

## 9. How to Verify Tables

Run the schema verification script to inspect all 16 tables, lookup counts, foreign keys, indexes, check constraints, and triggers:

```bash
psql -U postgres -d clauselens_db -v ON_ERROR_STOP=1 -f scripts/verify_database.sql
```

---

## 10. How the Database Connects to Django

Member 2 configures `DATABASES` in Django `settings.py` using environment variables from `.env`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "clauselens_db"),
        "USER": os.environ.get("DB_USER", "clauselens_app"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}
```

See [API_DATABASE_MAPPING.md](file:///C:/Users/User/.gemini/antigravity/scratch/ClauseLens/database/docs/API_DATABASE_MAPPING.md) for full model-to-table mappings and migration rules.

---

## 11. How to Run Database Tests

Run all three PostgreSQL validation suites (constraint tests and relationship/retention tests automatically roll back at the end):

```bash
psql -U postgres -d clauselens_db -v ON_ERROR_STOP=1 -f tests/test_constraints.sql
psql -U postgres -d clauselens_db -v ON_ERROR_STOP=1 -f tests/test_relationships.sql
psql -U postgres -d clauselens_db -v ON_ERROR_STOP=1 -f tests/test_queries.sql
```

---

## Directory Reference

- Schema DDL: `schema/01_users.sql` – `schema/10_monitoring.sql`
- Queries: `queries/*.sql`
- Seed Data: `seed/*.sql`
- Diagrams: [er_diagram.mmd](file:///C:/Users/User/.gemini/antigravity/scratch/ClauseLens/database/diagrams/er_diagram.mmd), [database_architecture.mmd](file:///C:/Users/User/.gemini/antigravity/scratch/ClauseLens/database/diagrams/database_architecture.mmd)
- Documentation: [DATA_DICTIONARY.md](file:///C:/Users/User/.gemini/antigravity/scratch/ClauseLens/database/docs/DATA_DICTIONARY.md), [DATABASE_DESIGN.md](file:///C:/Users/User/.gemini/antigravity/scratch/ClauseLens/database/docs/DATABASE_DESIGN.md), [API_DATABASE_MAPPING.md](file:///C:/Users/User/.gemini/antigravity/scratch/ClauseLens/database/docs/API_DATABASE_MAPPING.md)
