-- =============================================================================
-- ClauseLens Validation Tests - tests/test_queries.sql
-- Purpose: Executes core analytical queries against demonstration seed data
--          and asserts expected non-empty results for Alex, Sarah, and John.
-- Execution:
--   psql -U postgres -d clauselens_db -v ON_ERROR_STOP=1 -f database/tests/test_queries.sql
-- =============================================================================

DO $$
DECLARE
    v_alex_id       BIGINT;
    v_sarah_id      BIGINT;
    v_john_id       BIGINT;
    v_google_doc_id BIGINT;
    v_amazon_doc_id BIGINT;
    v_count         INTEGER;
    v_score         NUMERIC;
BEGIN
    SELECT id INTO v_alex_id FROM users WHERE username = 'alex_in';
    SELECT id INTO v_sarah_id FROM users WHERE username = 'sarah_us';
    SELECT id INTO v_john_id FROM users WHERE username = 'john_eu';
    SELECT id INTO v_google_doc_id FROM documents WHERE document_name = '[DEMO] Google Privacy Policy (Illustrative Sample)';
    SELECT id INTO v_amazon_doc_id FROM documents WHERE document_name = '[DEMO] Amazon Privacy Policy (Illustrative Sample)';

    IF v_alex_id IS NULL OR v_google_doc_id IS NULL THEN
        RAISE EXCEPTION 'Seed data not loaded. Run seed scripts before test_queries.sql.';
    END IF;

    -- Q1: Documents belonging to Alex
    SELECT COUNT(*) INTO v_count
    FROM documents d
    WHERE d.user_id = v_alex_id AND d.is_deleted = FALSE;
    IF v_count < 1 THEN
        RAISE EXCEPTION 'Q1 FAILED: Expected >= 1 document for Alex.';
    END IF;

    -- Q2: Clauses from Google Demo document
    SELECT COUNT(*) INTO v_count
    FROM clauses c
    JOIN clause_summaries cs ON cs.clause_id = c.id
    WHERE c.document_id = v_google_doc_id;
    IF v_count < 2 THEN
        RAISE EXCEPTION 'Q2 FAILED: Expected >= 2 summarized clauses for Google Demo document.';
    END IF;

    -- Q3 & Q14: High-risk clauses across documents (severity >= 0.700)
    SELECT COUNT(*) INTO v_count
    FROM clauses
    WHERE severity_score >= 0.700;
    IF v_count < 4 THEN
        RAISE EXCEPTION 'Q3/Q14 FAILED: Expected >= 4 high-risk demo clauses.';
    END IF;

    -- Q4: Personalized clause rankings for Sarah
    SELECT MAX(relevance_score) INTO v_score
    FROM personalized_risks
    WHERE user_id = v_sarah_id;
    IF v_score IS NULL OR v_score < 0.800 THEN
        RAISE EXCEPTION 'Q4 FAILED: Expected high personalized relevance score for Sarah.';
    END IF;

    -- Q5: Document analysis statistics
    SELECT overall_risk_score INTO v_score
    FROM analysis_results
    WHERE document_id = v_google_doc_id
    ORDER BY created_at DESC LIMIT 1;
    IF v_score IS NULL OR v_score <= 0 THEN
        RAISE EXCEPTION 'Q5 FAILED: Missing analysis_results for Google Demo document.';
    END IF;

    -- Q6 & Q7: Notifications and unread count for Alex
    SELECT COUNT(*) INTO v_count
    FROM notifications
    WHERE user_id = v_alex_id AND is_read = FALSE;
    IF v_count < 1 THEN
        RAISE EXCEPTION 'Q6/Q7 FAILED: Expected >= 1 unread notification for Alex.';
    END IF;

    -- Q8: Monitored policies for Sarah (including shared Google policy)
    SELECT COUNT(*) INTO v_count
    FROM monitored_policies
    WHERE user_id = v_sarah_id AND monitoring_status = 'Active';
    IF v_count < 2 THEN
        RAISE EXCEPTION 'Q8 FAILED: Expected >= 2 active monitored policies for Sarah.';
    END IF;

    -- Q9, Q10, Q11, Q12: Policy versions & Added/Removed/Modified changes
    SELECT COUNT(*) INTO v_count FROM policy_versions WHERE document_id = v_google_doc_id;
    IF v_count < 2 THEN
        RAISE EXCEPTION 'Q9 FAILED: Expected >= 2 policy versions for Google Demo document.';
    END IF;

    SELECT COUNT(*) INTO v_count FROM policy_changes WHERE document_id = v_amazon_doc_id AND change_type = 'Added';
    IF v_count < 1 THEN
        RAISE EXCEPTION 'Q10 FAILED: Expected >= 1 Added clause on Amazon Demo document.';
    END IF;

    SELECT COUNT(*) INTO v_count FROM policy_changes WHERE document_id = v_google_doc_id AND change_type = 'Removed';
    IF v_count < 1 THEN
        RAISE EXCEPTION 'Q11 FAILED: Expected >= 1 Removed clause on Google Demo document.';
    END IF;

    SELECT COUNT(*) INTO v_count FROM policy_changes WHERE document_id = v_google_doc_id AND change_type = 'Modified';
    IF v_count < 1 THEN
        RAISE EXCEPTION 'Q12 FAILED: Expected >= 1 Modified clause on Google Demo document.';
    END IF;

    -- Q13: Recent policy changes for Sarah's monitored policies
    SELECT COUNT(*) INTO v_count
    FROM policy_changes pc
    JOIN monitored_policies mp ON mp.document_id = pc.document_id
    WHERE mp.user_id = v_sarah_id;
    IF v_count < 2 THEN
        RAISE EXCEPTION 'Q13 FAILED: Expected >= 2 policy changes across Sarah''s monitored policies.';
    END IF;

    RAISE NOTICE 'ALL QUERY VALIDATION ASSERTIONS PASSED SUCCESSFULLY.';
END
$$;
