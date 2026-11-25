-- =============================================================================
-- ClauseLens Queries - queries/notification_queries.sql
-- Purpose: Retrieve user alerts, count unread notifications, and mark read.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Query 6: Get all notifications for a user (ordered newest first)
-- Parameters:
--   $1 (BIGINT)  - user_id
--   $2 (INTEGER) - limit (e.g., 50)
--   $3 (INTEGER) - offset (e.g., 0)
-- -----------------------------------------------------------------------------
SELECT
    n.id AS notification_id,
    n.policy_change_id,
    n.title,
    n.message,
    n.alert_score,
    n.severity,
    n.is_read,
    n.created_at,
    d.id AS document_id,
    d.document_name,
    pc.change_type,
    pc.change_direction
FROM notifications n
LEFT JOIN policy_changes pc
    ON pc.id = n.policy_change_id
LEFT JOIN documents d
    ON d.id = pc.document_id
WHERE n.user_id = $1
ORDER BY n.is_read ASC, n.created_at DESC
LIMIT $2 OFFSET $3;

-- -----------------------------------------------------------------------------
-- Query 7: Get unread notification count for a user
-- Parameters:
--   $1 (BIGINT) - user_id
-- -----------------------------------------------------------------------------
SELECT
    COUNT(*) AS unread_count,
    COUNT(*) FILTER (WHERE severity IN ('High', 'Critical')) AS unread_critical_or_high_count
FROM notifications
WHERE user_id = $1
  AND is_read = FALSE;

-- -----------------------------------------------------------------------------
-- Supplemental Update: Mark a single notification as read (ownership-safe)
-- Parameters:
--   $1 (BIGINT) - notification_id
--   $2 (BIGINT) - user_id
-- -----------------------------------------------------------------------------
UPDATE notifications
SET is_read = TRUE
WHERE id = $1
  AND user_id = $2
  AND is_read = FALSE
RETURNING id, is_read;
