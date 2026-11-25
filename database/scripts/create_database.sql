-- =============================================================================
-- ClauseLens Database Creation Script - scripts/create_database.sql
-- Usage:
--   psql -U postgres -f database/scripts/create_database.sql
-- Note:
--   Run connected to the default 'postgres' maintenance database as a superuser
--   or role with CREATEDB privileges. No passwords are stored in this file.
-- =============================================================================

SELECT 'CREATE DATABASE clauselens_db WITH ENCODING ''UTF8'' TEMPLATE template0'
WHERE NOT EXISTS (
    SELECT 1 FROM pg_database WHERE datname = 'clauselens_db'
)\gexec

\connect clauselens_db

-- Enable useful standard extensions if permitted
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Execute schema files in strict dependency order (relative to this script)
\ir ../schema/01_users.sql
\ir ../schema/02_profiles.sql
\ir ../schema/03_documents.sql
\ir ../schema/04_clauses.sql
\ir ../schema/05_analysis_results.sql
\ir ../schema/06_personalized_risks.sql
\ir ../schema/07_policy_versions.sql
\ir ../schema/08_policy_changes.sql
\ir ../schema/09_notifications.sql
\ir ../schema/10_monitoring.sql
