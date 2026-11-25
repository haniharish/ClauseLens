-- =============================================================================
-- ClauseLens Queries - queries/dashboard_queries.sql
-- Purpose: KPI summary metrics and user dashboard statistics.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Query 15: Generate dashboard statistics for a user
-- Parameters:
--   $1 (BIGINT) - user_id
-- -----------------------------------------------------------------------------
WITH user_docs AS (
    SELECT d.id
    FROM documents d
    WHERE d.is_deleted = FALSE
      AND (
          d.user_id = $1
          OR EXISTS (
              SELECT 1
              FROM monitored_policies mp
              WHERE mp.document_id = d.id AND mp.user_id = $1
          )
      )
),
latest_doc_analyses AS (
    SELECT DISTINCT ON (ar.document_id)
        ar.document_id,
        ar.total_clauses,
        ar.high_risk_count,
        ar.medium_risk_count,
        ar.low_risk_count,
        ar.overall_risk_score
    FROM analysis_results ar
    INNER JOIN user_docs ud ON ud.id = ar.document_id
    WHERE ar.analysis_status = 'Completed'
    ORDER BY ar.document_id, ar.created_at DESC
)
SELECT
    u.id AS user_id,
    u.full_name,
    ag.label AS age_group,
    j.name AS jurisdiction,
    (SELECT COUNT(*) FROM documents d WHERE d.user_id = $1 AND d.is_deleted = FALSE) AS uploaded_documents_count,
    (SELECT COUNT(*) FROM monitored_policies mp WHERE mp.user_id = $1 AND mp.monitoring_status = 'Active') AS active_monitored_policies_count,
    (SELECT COUNT(*) FROM notifications n WHERE n.user_id = $1 AND n.is_read = FALSE) AS unread_notifications_count,
    COALESCE((SELECT ROUND(AVG(lda.overall_risk_score), 2) FROM latest_doc_analyses lda), 0.00) AS avg_overall_risk_score,
    COALESCE((SELECT SUM(lda.high_risk_count) FROM latest_doc_analyses lda), 0) AS total_high_risk_clauses,
    COALESCE((SELECT SUM(lda.medium_risk_count) FROM latest_doc_analyses lda), 0) AS total_medium_risk_clauses,
    COALESCE((SELECT SUM(lda.low_risk_count) FROM latest_doc_analyses lda), 0) AS total_low_risk_clauses,
    (
        SELECT COUNT(*)
        FROM policy_changes pc
        INNER JOIN user_docs ud ON ud.id = pc.document_id
        WHERE pc.change_type IN ('Added', 'Removed', 'Modified')
          AND pc.detected_at >= CURRENT_TIMESTAMP - INTERVAL '30 days'
    ) AS recent_policy_changes_30d
FROM users u
LEFT JOIN user_profiles up ON up.user_id = u.id
LEFT JOIN age_groups ag ON ag.id = up.age_group_id
LEFT JOIN jurisdictions j ON j.id = up.jurisdiction_id
WHERE u.id = $1;
