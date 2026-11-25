-- =============================================================================
-- ClauseLens Database Verification Script - scripts/verify_database.sql
-- Purpose: Inspects tables, lookup counts, foreign keys, unique constraints,
--          check constraints, indexes, and triggers in clauselens_db.
-- Usage:
--   psql -U postgres -d clauselens_db -f database/scripts/verify_database.sql
-- =============================================================================

\echo '=== 1. Verifying Expected ClauseLens Tables ==='
WITH expected_tables(table_name) AS (
    VALUES
        ('users'),
        ('age_groups'),
        ('jurisdictions'),
        ('intended_use_categories'),
        ('user_profiles'),
        ('user_profile_intended_uses'),
        ('documents'),
        ('clause_categories'),
        ('clauses'),
        ('clause_summaries'),
        ('analysis_results'),
        ('personalized_risks'),
        ('policy_versions'),
        ('policy_changes'),
        ('notifications'),
        ('monitored_policies')
)
SELECT
    e.table_name,
    CASE WHEN t.tablename IS NOT NULL THEN 'OK' ELSE 'MISSING' END AS status
FROM expected_tables e
LEFT JOIN pg_tables t
    ON t.schemaname = 'public' AND t.tablename = e.table_name
ORDER BY e.table_name;

\echo '=== 2. Verifying Canonical Lookup Seed Counts ==='
SELECT 'age_groups' AS lookup_table, COUNT(*) AS row_count FROM age_groups
UNION ALL
SELECT 'jurisdictions', COUNT(*) FROM jurisdictions
UNION ALL
SELECT 'intended_use_categories', COUNT(*) FROM intended_use_categories
UNION ALL
SELECT 'clause_categories', COUNT(*) FROM clause_categories;

\echo '=== 3. Verifying Foreign Key Constraints ==='
SELECT
    tc.table_name,
    tc.constraint_name,
    kcu.column_name,
    ccu.table_name AS references_table,
    ccu.column_name AS references_column,
    rc.delete_rule
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
JOIN information_schema.referential_constraints rc
    ON rc.constraint_name = tc.constraint_name
    AND rc.constraint_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_name;

\echo '=== 4. Verifying Indexes ==='
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

\echo '=== 5. Verifying Check Constraints & Triggers ==='
SELECT
    tc.table_name,
    tc.constraint_name
FROM information_schema.table_constraints tc
WHERE tc.constraint_type = 'CHECK'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_name;

SELECT
    event_object_table AS table_name,
    trigger_name,
    action_timing,
    event_manipulation
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

\echo '=== 6. Hard-Failure Integrity Check ==='
DO $$
DECLARE
    missing_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO missing_count
    FROM (
        VALUES
            ('users'), ('age_groups'), ('jurisdictions'),
            ('intended_use_categories'), ('user_profiles'),
            ('user_profile_intended_uses'), ('documents'),
            ('clause_categories'), ('clauses'), ('clause_summaries'),
            ('analysis_results'), ('personalized_risks'),
            ('policy_versions'), ('policy_changes'),
            ('notifications'), ('monitored_policies')
    ) AS req(name)
    LEFT JOIN pg_tables t ON t.schemaname = 'public' AND t.tablename = req.name
    WHERE t.tablename IS NULL;

    IF missing_count > 0 THEN
        RAISE EXCEPTION 'Database verification failed: % required tables are missing.', missing_count;
    END IF;
END
$$;
