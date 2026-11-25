-- =============================================================================
-- ClauseLens Queries - queries/document_queries.sql
-- Security: All queries use PostgreSQL positional parameters ($1, $2, ...)
--           and enforce user ownership or public-policy visibility.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Query 1: Get all active documents belonging to a user (with latest analysis)
-- Parameters:
--   $1 (BIGINT) - user_id
-- -----------------------------------------------------------------------------
SELECT
    d.id AS document_id,
    d.document_name,
    d.document_type,
    d.source_type,
    d.file_path,
    d.policy_url,
    d.processing_status,
    d.is_public_policy,
    d.created_at,
    d.updated_at,
    ar.total_clauses,
    ar.high_risk_count,
    ar.medium_risk_count,
    ar.low_risk_count,
    ar.overall_risk_score,
    ar.analysis_status
FROM documents d
LEFT JOIN LATERAL (
    SELECT
        a.total_clauses,
        a.high_risk_count,
        a.medium_risk_count,
        a.low_risk_count,
        a.overall_risk_score,
        a.analysis_status
    FROM analysis_results a
    WHERE a.document_id = d.id
    ORDER BY a.created_at DESC
    LIMIT 1
) ar ON TRUE
WHERE d.user_id = $1
  AND d.is_deleted = FALSE
ORDER BY d.created_at DESC;

-- -----------------------------------------------------------------------------
-- Query 5: Get document analysis statistics (summary + category breakdown)
-- Parameters:
--   $1 (BIGINT) - document_id
--   $2 (BIGINT) - requesting user_id (enforces ownership or public/monitored access)
-- -----------------------------------------------------------------------------
WITH latest_analysis AS (
    SELECT
        ar.id,
        ar.document_id,
        ar.total_clauses,
        ar.high_risk_count,
        ar.medium_risk_count,
        ar.low_risk_count,
        ar.overall_risk_score,
        ar.analysis_status,
        ar.created_at AS analyzed_at
    FROM analysis_results ar
    WHERE ar.document_id = $1
    ORDER BY ar.created_at DESC
    LIMIT 1
)
SELECT
    d.id AS document_id,
    d.document_name,
    d.document_type,
    d.processing_status,
    la.total_clauses,
    la.high_risk_count,
    la.medium_risk_count,
    la.low_risk_count,
    la.overall_risk_score,
    la.analysis_status,
    la.analyzed_at,
    COALESCE(ROUND(AVG(c.severity_score), 3), 0.000) AS avg_clause_severity,
    COALESCE(MAX(c.severity_score), 0.000) AS max_clause_severity
FROM documents d
LEFT JOIN latest_analysis la ON la.document_id = d.id
LEFT JOIN clauses c ON c.document_id = d.id
WHERE d.id = $1
  AND d.is_deleted = FALSE
  AND (
      d.user_id = $2
      OR d.is_public_policy = TRUE
      OR EXISTS (
          SELECT 1
          FROM monitored_policies mp
          WHERE mp.document_id = d.id AND mp.user_id = $2
      )
  )
GROUP BY
    d.id, d.document_name, d.document_type, d.processing_status,
    la.total_clauses, la.high_risk_count, la.medium_risk_count,
    la.low_risk_count, la.overall_risk_score, la.analysis_status, la.analyzed_at;
