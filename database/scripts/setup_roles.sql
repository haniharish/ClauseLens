-- =============================================================================
-- ClauseLens Least-Privilege Role Setup - scripts/setup_roles.sql
-- Usage (pass password securely at runtime; never commit credentials):
--   psql -U postgres -d clauselens_db \
--     -v app_password="REPLACE_AT_RUNTIME" \
--     -v ro_password="REPLACE_AT_RUNTIME" \
--     -f database/scripts/setup_roles.sql
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'clauselens_app') THEN
        CREATE ROLE clauselens_app WITH LOGIN PASSWORD NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'clauselens_readonly') THEN
        CREATE ROLE clauselens_readonly WITH LOGIN PASSWORD NULL;
    END IF;
END
$$;

-- Apply runtime-supplied passwords via psql variables if provided
\if :{?app_password}
ALTER ROLE clauselens_app WITH PASSWORD :'app_password';
\endif
\if :{?ro_password}
ALTER ROLE clauselens_readonly WITH PASSWORD :'ro_password';
\endif

-- Restrict default public schema creation privileges
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE clauselens_db FROM PUBLIC;

-- Application role: least-privilege DML (no DROP/TRUNCATE/DDL in production)
GRANT CONNECT ON DATABASE clauselens_db TO clauselens_app;
GRANT USAGE ON SCHEMA public TO clauselens_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO clauselens_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO clauselens_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO clauselens_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO clauselens_app;

-- Read-only analytics/audit role
GRANT CONNECT ON DATABASE clauselens_db TO clauselens_readonly;
GRANT USAGE ON SCHEMA public TO clauselens_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO clauselens_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO clauselens_readonly;
