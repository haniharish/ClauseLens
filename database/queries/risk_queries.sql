-- =============================================================================
-- ClauseLens Queries - queries/risk_queries.sql
-- Purpose: Personalized clause relevance rankings and profile-aware analytics.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Query 4: Get personalized clause rankings for a user on a document
-- Parameters:
--   $1 (BIGINT) - user_id
--   $2 (BIGINT) - document_id
-- -----------------------------------------------------------------------------
SELECT
    pr.id AS personalized_risk_id,
    c.id AS clause_id,
    c.clause_order,
    c.clause_title,
    cc.name AS category_name,
    c.severity_score AS base_severity_score,
    pr.relevance_score,
    pr.risk_level,
    pr.why_it_matters,
    cs.simple_explanation,
    ag.label AS user_age_group,
    j.name AS user_jurisdiction
FROM personalized_risks pr
INNER JOIN clauses c
    ON c.id = pr.clause_id
INNER JOIN clause_categories cc
    ON cc.id = c.category_id
INNER JOIN user_profiles up
    ON up.user_id = pr.user_id
INNER JOIN age_groups ag
    ON ag.id = up.age_group_id
INNER JOIN jurisdictions j
    ON j.id = up.jurisdiction_id
LEFT JOIN LATERAL (
    SELECT s.simple_explanation
    FROM clause_summaries s
    WHERE s.clause_id = c.id
    ORDER BY s.summary_version DESC, s.created_at DESC
    LIMIT 1
) cs ON TRUE
WHERE pr.user_id = $1
  AND c.document_id = $2
ORDER BY pr.relevance_score DESC, c.severity_score DESC;

-- -----------------------------------------------------------------------------
-- Supplemental Risk Query: Category-level personalized risk breakdown for user
-- Parameters:
--   $1 (BIGINT) - user_id
-- -----------------------------------------------------------------------------
SELECT
    cc.name AS category_name,
    COUNT(pr.id) AS evaluated_clauses,
    ROUND(AVG(pr.relevance_score), 3) AS avg_relevance_score,
    MAX(pr.relevance_score) AS max_relevance_score,
    COUNT(*) FILTER (WHERE pr.risk_level IN ('High', 'Critical')) AS high_or_critical_count
FROM personalized_risks pr
INNER JOIN clauses c
    ON c.id = pr.clause_id
INNER JOIN clause_categories cc
    ON cc.id = c.category_id
WHERE pr.user_id = $1
GROUP BY cc.id, cc.name
ORDER BY avg_relevance_score DESC, high_or_critical_count DESC;
