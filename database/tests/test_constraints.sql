-- =============================================================================
-- ClauseLens Validation Tests - tests/test_constraints.sql
-- Purpose: Verifies PKs, unique constraints, NOT NULLs, lookup FKs, score
--          ranges, change_type rules, and version/notification deduplication.
-- Execution:
--   psql -U postgres -d clauselens_db -v ON_ERROR_STOP=1 -f database/tests/test_constraints.sql
-- Note: Uses SAVEPOINT/EXCEPTION blocks inside a rolled-back transaction so
--       no test artifacts persist after execution.
-- =============================================================================

BEGIN;

DO $$
DECLARE
    v_user_id       BIGINT;
    v_doc_id        BIGINT;
    v_cat_id        BIGINT;
    v_clause_id     BIGINT;
    v_ver1_id       BIGINT;
    v_ver2_id       BIGINT;
    v_change_id     BIGINT;
    v_ag_id         BIGINT;
    v_jur_id        BIGINT;
BEGIN
    SELECT id INTO v_user_id FROM users WHERE username = 'alex_in';
    SELECT id INTO v_doc_id FROM documents WHERE document_name = '[DEMO] Google Privacy Policy (Illustrative Sample)';
    SELECT id INTO v_cat_id FROM clause_categories WHERE code = 'data_sharing';
    SELECT id INTO v_clause_id FROM clauses WHERE document_id = v_doc_id LIMIT 1;
    SELECT id INTO v_ag_id FROM age_groups WHERE code = '18_64';
    SELECT id INTO v_jur_id FROM jurisdictions WHERE code = 'IN';

    IF v_user_id IS NULL OR v_doc_id IS NULL OR v_clause_id IS NULL THEN
        RAISE EXCEPTION 'Seed data must be loaded before running test_constraints.sql';
    END IF;

    -- 1. Primary Key uniqueness
    BEGIN
        INSERT INTO users (id, username, full_name, email, password)
        VALUES (v_user_id, 'pk_dup_user', 'Dup PK', 'pkdup@clauselens.local', 'pbkdf2_sha256$720000$salt$hashvalue1234567890');
        RAISE EXCEPTION 'TEST FAILED: Duplicate primary key on users was allowed';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'PASS [1]: Primary key uniqueness enforced on users.';
    END;

    -- 2. Unique email constraint
    BEGIN
        INSERT INTO users (username, full_name, email, password)
        VALUES ('unique_email_test', 'Test User', 'alex.demo@clauselens.local', 'pbkdf2_sha256$720000$salt$hashvalue1234567890');
        RAISE EXCEPTION 'TEST FAILED: Duplicate email was allowed';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'PASS [2]: Unique email constraint enforced.';
    END;

    -- 3. Required fields (NOT NULL)
    BEGIN
        INSERT INTO documents (user_id, document_name, document_type, source_type, policy_url)
        VALUES (v_user_id, NULL, 'Privacy Policy', 'URL', 'https://example.com/policy');
        RAISE EXCEPTION 'TEST FAILED: NULL document_name was allowed';
    EXCEPTION WHEN not_null_violation THEN
        RAISE NOTICE 'PASS [3]: Required NOT NULL field enforced on documents.document_name.';
    END;

    -- 4. Valid age groups (FK check)
    BEGIN
        INSERT INTO users (username, full_name, email, password)
        VALUES ('tmp_ag_user', 'Temp Age', 'tmpag@clauselens.local', 'pbkdf2_sha256$720000$salt$hashvalue1234567890')
        RETURNING id INTO v_user_id;

        INSERT INTO user_profiles (user_id, age_group_id, jurisdiction_id)
        VALUES (v_user_id, 999999, v_jur_id);
        RAISE EXCEPTION 'TEST FAILED: Invalid age_group_id was allowed';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'PASS [4]: Valid age_group_id foreign key enforced.';
    END;

    -- 5. Valid jurisdiction values (FK check)
    BEGIN
        INSERT INTO user_profiles (user_id, age_group_id, jurisdiction_id)
        VALUES (v_user_id, v_ag_id, 999999);
        RAISE EXCEPTION 'TEST FAILED: Invalid jurisdiction_id was allowed';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'PASS [5]: Valid jurisdiction_id foreign key enforced.';
    END;

    -- 6. Valid clause categories (FK check)
    BEGIN
        INSERT INTO clauses (document_id, category_id, clause_title, original_text, severity_score, clause_order)
        VALUES (v_doc_id, 999999, 'Invalid Cat', 'Some legal text', 0.500, 999);
        RAISE EXCEPTION 'TEST FAILED: Invalid category_id was allowed';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'PASS [6]: Valid clause category_id foreign key enforced.';
    END;

    -- 7a. Valid clause severity score range (0..1)
    BEGIN
        INSERT INTO clauses (document_id, category_id, clause_title, original_text, severity_score, clause_order)
        VALUES (v_doc_id, v_cat_id, 'Out of Range', 'Some legal text', 1.250, 998);
        RAISE EXCEPTION 'TEST FAILED: severity_score > 1.0 was allowed';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'PASS [7a]: Clause severity_score range (0..1) enforced.';
    END;

    -- 7b. Valid personalized relevance_score range (0..1)
    BEGIN
        INSERT INTO personalized_risks (user_id, clause_id, relevance_score, risk_level, why_it_matters)
        VALUES (v_user_id, v_clause_id, -0.100, 'Low', 'Negative score should fail');
        RAISE EXCEPTION 'TEST FAILED: Negative relevance_score was allowed';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'PASS [7b]: Personalized relevance_score range (0..1) enforced.';
    END;

    -- 8. Valid change_types & Added/Removed clause presence rules
    SELECT id INTO v_ver1_id FROM policy_versions WHERE document_id = v_doc_id AND version_number = 'v1.0';
    SELECT id INTO v_ver2_id FROM policy_versions WHERE document_id = v_doc_id AND version_number = 'v2.0';

    BEGIN
        INSERT INTO policy_changes (
            document_id, old_version_id, new_version_id, old_clause_id, new_clause_id,
            change_type, change_direction, magnitude
        )
        VALUES (
            v_doc_id, v_ver1_id, v_ver2_id, v_clause_id, v_clause_id,
            'Added', 'Less Favorable', 0.500
        );
        RAISE EXCEPTION 'TEST FAILED: Added change_type with non-null old_clause_id was allowed';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'PASS [8a]: Added change_type requires old_clause_id IS NULL.';
    END;

    BEGIN
        INSERT INTO policy_changes (
            document_id, old_version_id, new_version_id, old_clause_id, new_clause_id,
            change_type, change_direction, magnitude
        )
        VALUES (
            v_doc_id, v_ver1_id, v_ver2_id, NULL, v_clause_id,
            'InvalidType', 'Neutral', 0.500
        );
        RAISE EXCEPTION 'TEST FAILED: Invalid change_type was allowed';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'PASS [8b]: Invalid change_type rejected.';
    END;

    -- 9. No duplicate policy versions for the same document and content_hash
    BEGIN
        INSERT INTO policy_versions (
            document_id, version_number, version_sequence, version_text, content_hash
        )
        VALUES (
            v_doc_id, 'v9.9', 99, 'Duplicate hash test',
            '1111111111111111111111111111111111111111111111111111111111111111'
        );
        RAISE EXCEPTION 'TEST FAILED: Duplicate (document_id, content_hash) was allowed';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'PASS [9]: Duplicate content_hash per document prevented.';
    END;

    -- 10. Prevent duplicate notifications for same (user_id, policy_change_id)
    SELECT id INTO v_change_id FROM policy_changes WHERE document_id = v_doc_id LIMIT 1;
    INSERT INTO notifications (user_id, policy_change_id, title, message, alert_score, severity)
    VALUES (v_user_id, v_change_id, 'First Alert', 'Valid alert', 0.700, 'High');

    BEGIN
        INSERT INTO notifications (user_id, policy_change_id, title, message, alert_score, severity)
        VALUES (v_user_id, v_change_id, 'Dup Alert', 'Should fail', 0.700, 'High');
        RAISE EXCEPTION 'TEST FAILED: Duplicate notification for same user and policy_change was allowed';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'PASS [10]: Duplicate notification for same (user_id, policy_change_id) prevented.';
    END;
END
$$;

ROLLBACK;
