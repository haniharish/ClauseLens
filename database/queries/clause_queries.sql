-- =============================================================================
-- ClauseLens Queries - queries/clause_queries.sql
-- Security: Parameterized SQL ($1, $2, ...) preventing SQL injection.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Query 2: Get all clauses from a document (with category & latest AI summary)
-- Parameters:
--   $1 (BIGINT) - document_id
--   $2 (VARCHAR) - summary_language (e.g., 'en')
-- -----------------------------------------------------------------------------
SELECT
    c.id AS clause_id,
    c.document_id,
    c.clause_order,
    c.clause_title,
    cc.code AS category_code,
    cc.name AS category_name,
    c.severity_score,
    c.original_text,
    cs.simple_explanation,
    cs.model_name AS summary_model,
    cs.summary_version,
    c.created_at
FROM clauses c
INNER JOIN clause_categories cc
    ON cc.id = c.category_id
LEFT JOIN LATERAL (
    SELECT
        s.simple_explanation,
        s.model_name,
        s.summary_version
    FROM clause_summaries s
    WHERE s.clause_id = c.id
      AND s.summary_language = $2
    ORDER BY s.summary_version DESC, s.created_at DESC
    LIMIT 1
) cs ON TRUE
WHERE c.document_id = $1
ORDER BY c.clause_order ASC;

-- -----------------------------------------------------------------------------
-- Query 3: Get the highest-risk clauses for a specific document
-- Parameters:
--   $1 (BIGINT)  - document_id
--   $2 (INTEGER) - limit (e.g., 5 or 10)
-- -----------------------------------------------------------------------------
SELECT
    c.id AS clause_id,
    c.clause_order,
    c.clause_title,
    cc.name AS category_name,
    c.severity_score,
    c.original_text,
    cs.simple_explanation
FROM clauses c
INNER JOIN clause_categories cc
    ON cc.id = c.category_id
LEFT JOIN LATERAL (
    SELECT s.simple_explanation
    FROM clause_summaries s
    WHERE s.clause_id = c.id
    ORDER BY s.summary_version DESC, s.created_at DESC
    LIMIT 1
) cs ON TRUE
WHERE c.document_id = $1
ORDER BY c.severity_score DESC, c.clause_order ASC
LIMIT $2;

-- -----------------------------------------------------------------------------
-- Query 14: Get all high-risk clauses across documents accessible to a user
-- Parameters:
--   $1 (BIGINT)  - user_id
--   $2 (NUMERIC) - minimum severity_score threshold (e.g., 0.700)
--   $3 (INTEGER) - limit (e.g., 25)
-- -----------------------------------------------------------------------------
SELECT
    d.id AS document_id,
    d.document_name,
    d.document_type,
    c.id AS clause_id,
    c.clause_title,
    cc.name AS category_name,
    c.severity_score,
    pr.relevance_score,
    pr.risk_level AS personalized_risk_level,
    cs.simple_explanation
FROM clauses c
INNER JOIN documents d
    ON d.id = c.document_id
INNER JOIN clause_categories cc
    ON cc.id = c.category_id
LEFT JOIN personalized_risks pr
    ON pr.clause_id = c.id AND pr.user_id = $1
LEFT JOIN LATERAL (
    SELECT s.simple_explanation
    FROM clause_summaries s
    WHERE s.clause_id = c.id
    ORDER BY s.summary_version DESC, s.created_at DESC
    LIMIT 1
) cs ON TRUE
WHERE d.is_deleted = FALSE
  AND c.severity_score >= $2
  AND (
      d.user_id = $1
      OR d.is_public_policy = TRUE
      OR EXISTS (
          SELECT 1
          FROM monitored_policies mp
          WHERE mp.document_id = d.id AND mp.user_id = $1
      )
  )
ORDER BY c.severity_score DESC, COALESCE(pr.relevance_score, 0.000) DESC
LIMIT $3;
