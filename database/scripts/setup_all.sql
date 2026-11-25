-- =============================================================================
-- ClauseLens Full One-Shot Setup - scripts/setup_all.sql
-- Purpose: Creates clauselens_db, builds all 16 tables, loads demonstration
--          seed data, verifies schema integrity, and runs all SQL tests.
-- Usage:
--   psql -U postgres -v ON_ERROR_STOP=1 -f database/scripts/setup_all.sql
-- =============================================================================

\ir create_database.sql

\echo '=== Loading Demonstration Seed Data ==='
\ir ../seed/sample_users.sql
\ir ../seed/sample_documents.sql
\ir ../seed/sample_clauses.sql
\ir ../seed/sample_versions.sql

\echo '=== Verifying Database Structure ==='
\ir verify_database.sql

\echo '=== Running Validation Test Suites ==='
\ir ../tests/test_constraints.sql
\ir ../tests/test_relationships.sql
\ir ../tests/test_queries.sql

\echo '=== ClauseLens Database Setup Complete! ==='
