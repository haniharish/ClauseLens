-- =============================================================================
-- ClauseLens Queries - queries/version_queries.sql
-- Purpose: Policy version history, clause-level diffs (Added/Removed/Modified),
--          and monitored policy feeds.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Query 8: Get all monitored policies for a user (with latest version info)
-- Parameters:
--   $1 (BIGINT) - user_id
-- -----------------------------------------------------------------------------
SELECT
    mp.id AS monitoring_id,
    mp.document_id,
    d.document_name,
    d.document_type,
    mp.policy_url,
    mp.monitoring_status,
    mp.check_interval_hours,
    mp.last_checked_at,
    mp.next_check_at,
    lv.version_number AS latest_version_number,
    lv.content_hash AS latest_content_hash,
    lv.fetched_at AS latest_fetched_at
FROM monitored_policies mp
INNER JOIN documents d
    ON d.id = mp.document_id
LEFT JOIN LATERAL (
    SELECT
        pv.version_number,
        pv.content_hash,
        pv.fetched_at
    FROM policy_versions pv
    WHERE pv.document_id = mp.document_id
    ORDER BY pv.version_sequence DESC
    LIMIT 1
) lv ON TRUE
WHERE mp.user_id = $1
ORDER BY mp.updated_at DESC;

-- -----------------------------------------------------------------------------
-- Query 9: Get old and new policy versions for a document
-- Parameters:
--   $1 (BIGINT) - document_id
-- -----------------------------------------------------------------------------
SELECT
    pv.id AS version_id,
    pv.document_id,
    d.document_name,
    pv.version_number,
    pv.version_sequence,
    pv.content_hash,
    pv.stored_reference,
    pv.version_text,
    pv.fetched_at,
    pv.created_at
FROM policy_versions pv
INNER JOIN documents d
    ON d.id = pv.document_id
WHERE pv.document_id = $1
ORDER BY pv.version_sequence DESC;

-- -----------------------------------------------------------------------------
-- Query 10: Get added clauses between versions for a document
-- Parameters:
--   $1 (BIGINT) - document_id
-- -----------------------------------------------------------------------------
SELECT
    pc.id AS policy_change_id,
    ov.version_number AS old_version,
    nv.version_number AS new_version,
    nc.id AS new_clause_id,
    nc.clause_title AS added_clause_title,
    cc.name AS category_name,
    nc.original_text AS added_clause_text,
    pc.change_direction,
    pc.magnitude,
    pc.change_summary,
    pc.detected_at
FROM policy_changes pc
INNER JOIN policy_versions ov ON ov.id = pc.old_version_id
INNER JOIN policy_versions nv ON nv.id = pc.new_version_id
INNER JOIN clauses nc ON nc.id = pc.new_clause_id
INNER JOIN clause_categories cc ON cc.id = nc.category_id
WHERE pc.document_id = $1
  AND pc.change_type = 'Added'
ORDER BY pc.detected_at DESC, pc.magnitude DESC;

-- -----------------------------------------------------------------------------
-- Query 11: Get removed clauses between versions for a document
-- Parameters:
--   $1 (BIGINT) - document_id
-- -----------------------------------------------------------------------------
SELECT
    pc.id AS policy_change_id,
    ov.version_number AS old_version,
    nv.version_number AS new_version,
    oc.id AS old_clause_id,
    oc.clause_title AS removed_clause_title,
    cc.name AS category_name,
    oc.original_text AS removed_clause_text,
    pc.change_direction,
    pc.magnitude,
    pc.change_summary,
    pc.detected_at
FROM policy_changes pc
INNER JOIN policy_versions ov ON ov.id = pc.old_version_id
INNER JOIN policy_versions nv ON nv.id = pc.new_version_id
INNER JOIN clauses oc ON oc.id = pc.old_clause_id
INNER JOIN clause_categories cc ON cc.id = oc.category_id
WHERE pc.document_id = $1
  AND pc.change_type = 'Removed'
ORDER BY pc.detected_at DESC, pc.magnitude DESC;

-- -----------------------------------------------------------------------------
-- Query 12: Get modified clauses between versions for a document
-- Parameters:
--   $1 (BIGINT) - document_id
-- -----------------------------------------------------------------------------
SELECT
    pc.id AS policy_change_id,
    ov.version_number AS old_version,
    nv.version_number AS new_version,
    oc.id AS old_clause_id,
    oc.clause_title AS old_clause_title,
    oc.original_text AS old_text,
    oc.severity_score AS old_severity,
    nc.id AS new_clause_id,
    nc.clause_title AS new_clause_title,
    nc.original_text AS new_text,
    nc.severity_score AS new_severity,
    pc.change_direction,
    pc.magnitude,
    pc.change_summary,
    pc.detected_at
FROM policy_changes pc
INNER JOIN policy_versions ov ON ov.id = pc.old_version_id
INNER JOIN policy_versions nv ON nv.id = pc.new_version_id
INNER JOIN clauses oc ON oc.id = pc.old_clause_id
INNER JOIN clauses nc ON nc.id = pc.new_clause_id
WHERE pc.document_id = $1
  AND pc.change_type = 'Modified'
ORDER BY pc.detected_at DESC, pc.magnitude DESC;

-- -----------------------------------------------------------------------------
-- Query 13: Get recent policy changes across a user's monitored/owned policies
-- Parameters:
--   $1 (BIGINT)  - user_id
--   $2 (INTEGER) - limit (e.g., 20)
-- -----------------------------------------------------------------------------
SELECT
    pc.id AS policy_change_id,
    d.id AS document_id,
    d.document_name,
    ov.version_number AS old_version,
    nv.version_number AS new_version,
    pc.change_type,
    pc.change_direction,
    pc.magnitude,
    pc.change_summary,
    COALESCE(nc.clause_title, oc.clause_title) AS affected_clause_title,
    pc.detected_at
FROM policy_changes pc
INNER JOIN documents d ON d.id = pc.document_id
INNER JOIN policy_versions ov ON ov.id = pc.old_version_id
INNER JOIN policy_versions nv ON nv.id = pc.new_version_id
LEFT JOIN clauses oc ON oc.id = pc.old_clause_id
LEFT JOIN clauses nc ON nc.id = pc.new_clause_id
WHERE d.is_deleted = FALSE
  AND (
      d.user_id = $1
      OR EXISTS (
          SELECT 1
          FROM monitored_policies mp
          WHERE mp.document_id = d.id AND mp.user_id = $1
      )
  )
ORDER BY pc.detected_at DESC
LIMIT $2;
