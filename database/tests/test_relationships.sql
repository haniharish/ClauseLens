-- =============================================================================
-- ClauseLens Validation Tests - tests/test_relationships.sql
-- Purpose: Verifies 1:1, 1:N, M:N relationships, document ownership,
--          retention protection (ON DELETE RESTRICT on policy history), and
--          safe user deletion without destroying unrelated policy evidence.
-- Execution:
--   psql -U postgres -d clauselens_db -v ON_ERROR_STOP=1 -f database/tests/test_relationships.sql
-- =============================================================================

BEGIN;

DO $$
DECLARE
    v_temp_user_id    BIGINT;
    v_sarah_id        BIGINT;
    v_ag_id           BIGINT;
    v_jur_id          BIGINT;
    v_use_id          BIGINT;
    v_profile_id      BIGINT;
    v_shared_doc_id   BIGINT;
    v_cat_id          BIGINT;
    v_clause_id       BIGINT;
    v_ver1_id         BIGINT;
    v_ver2_id         BIGINT;
    v_change_id       BIGINT;
    v_doc_owner_after BIGINT;
    v_ver_count_after INTEGER;
    v_mon_count_after INTEGER;
BEGIN
    SELECT id INTO v_sarah_id FROM users WHERE username = 'sarah_us';
    SELECT id INTO v_ag_id FROM age_groups WHERE code = '18_64';
    SELECT id INTO v_jur_id FROM jurisdictions WHERE code = 'EU';
    SELECT id INTO v_use_id FROM intended_use_categories WHERE code = 'freelancer';
    SELECT id INTO v_cat_id FROM clause_categories WHERE code = 'data_sharing';

    -- 1. Create temporary user + 1:1 profile + M:N intended use
    INSERT INTO users (username, full_name, email, password)
    VALUES ('rel_temp_user', 'Relationship Tester', 'rel.test@clauselens.local', 'pbkdf2_sha256$720000$salt$hashvalue1234567890')
    RETURNING id INTO v_temp_user_id;

    INSERT INTO user_profiles (user_id, age_group_id, jurisdiction_id)
    VALUES (v_temp_user_id, v_ag_id, v_jur_id)
    RETURNING id INTO v_profile_id;

    -- Verify 1:1 profile uniqueness
    BEGIN
        INSERT INTO user_profiles (user_id, age_group_id, jurisdiction_id)
        VALUES (v_temp_user_id, v_ag_id, v_jur_id);
        RAISE EXCEPTION 'TEST FAILED: User was allowed to have two profiles (violates 1:1)';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'PASS [1]: 1:1 relationship users <-> user_profiles enforced.';
    END;

    INSERT INTO user_profile_intended_uses (user_profile_id, intended_use_id)
    VALUES (v_profile_id, v_use_id);

    -- 2. Temporary user uploads a shared public policy document
    INSERT INTO documents (
        user_id, document_name, document_type, policy_url, source_type, processing_status, is_public_policy
    )
    VALUES (
        v_temp_user_id, 'Shared Public Policy Test', 'Privacy Policy',
        'https://example.org/shared-privacy', 'URL', 'Completed', TRUE
    )
    RETURNING id INTO v_shared_doc_id;

    -- Verify document ownership
    IF NOT EXISTS (
        SELECT 1 FROM documents WHERE id = v_shared_doc_id AND user_id = v_temp_user_id
    ) THEN
        RAISE EXCEPTION 'TEST FAILED: Document ownership mismatch.';
    END IF;
    RAISE NOTICE 'PASS [2]: Document ownership verified.';

    -- 3. Add clauses, policy_versions, policy_changes, and second subscriber (sarah_us)
    INSERT INTO clauses (document_id, category_id, clause_title, original_text, severity_score, clause_order)
    VALUES (v_shared_doc_id, v_cat_id, 'Shared Clause 1', 'Shared policy clause text', 0.600, 1)
    RETURNING id INTO v_clause_id;

    INSERT INTO policy_versions (document_id, version_number, version_sequence, version_text, content_hash)
    VALUES (v_shared_doc_id, 'v1.0', 1, 'Version 1 text', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    RETURNING id INTO v_ver1_id;

    INSERT INTO policy_versions (document_id, version_number, version_sequence, version_text, content_hash)
    VALUES (v_shared_doc_id, 'v2.0', 2, 'Version 2 text', 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')
    RETURNING id INTO v_ver2_id;

    INSERT INTO policy_changes (
        document_id, old_version_id, new_version_id, old_clause_id, new_clause_id,
        change_type, change_direction, magnitude
    )
    VALUES (
        v_shared_doc_id, v_ver1_id, v_ver2_id, NULL, v_clause_id,
        'Added', 'Less Favorable', 0.600
    )
    RETURNING id INTO v_change_id;

    INSERT INTO monitored_policies (user_id, document_id, policy_url, monitoring_status)
    VALUES (v_sarah_id, v_shared_doc_id, 'https://example.org/shared-privacy', 'Active');

    -- 4. Verify ON DELETE RESTRICT protects historical policy_versions from document hard-delete
    BEGIN
        DELETE FROM documents WHERE id = v_shared_doc_id;
        RAISE EXCEPTION 'TEST FAILED: Document with policy_versions was hard-deleted!';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'PASS [3]: Historical policy evidence protected by ON DELETE RESTRICT.';
    END;

    -- 5. Delete temp_user and verify unrelated/shared policy history remains intact
    DELETE FROM users WHERE id = v_temp_user_id;

    SELECT user_id INTO v_doc_owner_after FROM documents WHERE id = v_shared_doc_id;
    SELECT COUNT(*) INTO v_ver_count_after FROM policy_versions WHERE document_id = v_shared_doc_id;
    SELECT COUNT(*) INTO v_mon_count_after FROM monitored_policies WHERE document_id = v_shared_doc_id AND user_id = v_sarah_id;

    IF v_doc_owner_after IS NOT NULL THEN
        RAISE EXCEPTION 'TEST FAILED: Expected documents.user_id to be anonymized (NULL) after user deletion.';
    END IF;

    IF v_ver_count_after <> 2 THEN
        RAISE EXCEPTION 'TEST FAILED: Policy versions were lost after uploader deletion (count=%).', v_ver_count_after;
    END IF;

    IF v_mon_count_after <> 1 THEN
        RAISE EXCEPTION 'TEST FAILED: Other user monitoring subscription was lost after uploader deletion.';
    END IF;

    RAISE NOTICE 'PASS [4]: Deleting user anonymizes ownership while preserving shared policy history and subscriber monitoring.';
END
$$;

ROLLBACK;
