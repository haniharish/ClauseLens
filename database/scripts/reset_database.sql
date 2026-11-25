-- =============================================================================
-- ClauseLens Database Reset Script (DEV/TEST ONLY) - scripts/reset_database.sql
-- WARNING: Permanently drops all ClauseLens tables and recreates the schema.
-- Never run against production data.
-- Usage:
--   psql -U postgres -d clauselens_db -f database/scripts/reset_database.sql
-- =============================================================================

BEGIN;

DROP TABLE IF EXISTS monitored_policies CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS policy_changes CASCADE;
DROP TABLE IF EXISTS policy_versions CASCADE;
DROP TABLE IF EXISTS personalized_risks CASCADE;
DROP TABLE IF EXISTS analysis_results CASCADE;
DROP TABLE IF EXISTS clause_summaries CASCADE;
DROP TABLE IF EXISTS clauses CASCADE;
DROP TABLE IF EXISTS clause_categories CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS user_profile_intended_uses CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS intended_use_categories CASCADE;
DROP TABLE IF EXISTS jurisdictions CASCADE;
DROP TABLE IF EXISTS age_groups CASCADE;
DROP TABLE IF EXISTS users CASCADE;

DROP FUNCTION IF EXISTS fn_set_updated_at() CASCADE;

COMMIT;

-- Recreate schema in dependency order (relative to this script)
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
