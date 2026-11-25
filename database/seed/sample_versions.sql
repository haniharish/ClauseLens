-- =============================================================================
-- ClauseLens Demonstration Seed Data - seed/sample_versions.sql
-- NOTICE: Fictional/illustrative version history, clause diffs, monitoring
--         subscriptions, and personalized notifications for demo purposes.
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- 1. Insert v1.0 and v2.0 policy versions (with valid 64-char SHA-256 hashes)
-- -----------------------------------------------------------------------------
INSERT INTO policy_versions (
    document_id, version_number, version_sequence, version_text, stored_reference, content_hash, fetched_at
)
SELECT
    d.id,
    v.version_number,
    v.version_sequence,
    v.version_text,
    v.stored_reference,
    v.content_hash,
    v.fetched_at
FROM (
    VALUES
        (
            '[DEMO] Google Privacy Policy (Illustrative Sample)',
            'v1.0',
            1,
            'DEMO SNAPSHOT v1.0: Initial baseline text covering standard analytics sharing and 18-month backup retention.',
            'snapshots/demo/google_privacy_v1.txt',
            '1111111111111111111111111111111111111111111111111111111111111111',
            CURRENT_TIMESTAMP - INTERVAL '45 days'
        ),
        (
            '[DEMO] Google Privacy Policy (Illustrative Sample)',
            'v2.0',
            2,
            'DEMO SNAPSHOT v2.0: Updated text expanding backup retention to 36 months and clarifying third-party ad partner telemetry.',
            'snapshots/demo/google_privacy_v2.txt',
            '2222222222222222222222222222222222222222222222222222222222222222',
            CURRENT_TIMESTAMP - INTERVAL '5 days'
        ),
        (
            '[DEMO] Amazon Privacy Policy (Illustrative Sample)',
            'v1.0',
            1,
            'DEMO SNAPSHOT v1.0: Baseline membership renewal and marketplace disclosure policy.',
            'snapshots/demo/amazon_privacy_v1.txt',
            '3333333333333333333333333333333333333333333333333333333333333333',
            CURRENT_TIMESTAMP - INTERVAL '30 days'
        ),
        (
            '[DEMO] Amazon Privacy Policy (Illustrative Sample)',
            'v1.1',
            2,
            'DEMO SNAPSHOT v1.1: Added automatic renewal rate-adjustment notice and seller logistics sharing updates.',
            'snapshots/demo/amazon_privacy_v1_1.txt',
            '4444444444444444444444444444444444444444444444444444444444444444',
            CURRENT_TIMESTAMP - INTERVAL '2 days'
        )
) AS v(document_name, version_number, version_sequence, version_text, stored_reference, content_hash, fetched_at)
JOIN documents d ON d.document_name = v.document_name
ON CONFLICT (document_id, version_number) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 2. Insert historical baseline/new clauses for diff examples (Added, Removed, Modified)
-- -----------------------------------------------------------------------------
INSERT INTO clauses (
    document_id, category_id, clause_title, original_text, severity_score, clause_order
)
SELECT d.id, cc.id, v.clause_title, v.original_text, v.severity_score, v.clause_order
FROM (
    VALUES
        (
            '[DEMO] Google Privacy Policy (Illustrative Sample)',
            'data_retention',
            'Legacy 18-Month Backup Retention (v1.0 Demo)',
            'ILLUSTRATIVE DEMO v1.0 TEXT: Diagnostic backup logs are purged after 18 months following account closure.',
            0.450,
            3
        ),
        (
            '[DEMO] Google Privacy Policy (Illustrative Sample)',
            'other',
            'Legacy Regional Opt-Out Fax Notice (Removed v1.0 Demo)',
            'ILLUSTRATIVE DEMO v1.0 TEXT: Users could previously submit regional opt-out requests via legacy postal or fax channels.',
            0.250,
            4
        ),
        (
            '[DEMO] Amazon Privacy Policy (Illustrative Sample)',
            'unilateral_change',
            'Immediate Price Notice Update (Added v1.1 Demo)',
            'ILLUSTRATIVE DEMO v1.1 TEXT: Updated subscription pricing takes effect on the next billing date following electronic notice.',
            0.760,
            3
        )
) AS v(document_name, category_code, clause_title, original_text, severity_score, clause_order)
JOIN documents d ON d.document_name = v.document_name
JOIN clause_categories cc ON cc.code = v.category_code
ON CONFLICT (document_id, clause_order) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 3. Insert policy_changes (Modified, Removed, Added)
-- -----------------------------------------------------------------------------
-- Modified clause: Legacy 18-Month -> Extended 36-Month Retention
INSERT INTO policy_changes (
    document_id, old_version_id, new_version_id, old_clause_id, new_clause_id,
    change_type, change_direction, magnitude, change_summary, detected_at
)
SELECT
    d.id,
    ov.id,
    nv.id,
    oc.id,
    nc.id,
    'Modified',
    'Less Favorable',
    0.650,
    'Retention window doubled from 18 months (v1.0) to 36 months (v2.0) in encrypted archival backups.',
    CURRENT_TIMESTAMP - INTERVAL '5 days'
FROM documents d
JOIN policy_versions ov ON ov.document_id = d.id AND ov.version_number = 'v1.0'
JOIN policy_versions nv ON nv.document_id = d.id AND nv.version_number = 'v2.0'
JOIN clauses oc ON oc.document_id = d.id AND oc.clause_title = 'Legacy 18-Month Backup Retention (v1.0 Demo)'
JOIN clauses nc ON nc.document_id = d.id AND nc.clause_title = 'Extended Operational & Backup Data Retention (Demo)'
WHERE d.document_name = '[DEMO] Google Privacy Policy (Illustrative Sample)'
  AND NOT EXISTS (
      SELECT 1 FROM policy_changes pc
      WHERE pc.old_version_id = ov.id AND pc.new_version_id = nv.id AND pc.change_type = 'Modified'
  );

-- Removed clause: Legacy Regional Opt-Out Fax Notice
INSERT INTO policy_changes (
    document_id, old_version_id, new_version_id, old_clause_id, new_clause_id,
    change_type, change_direction, magnitude, change_summary, detected_at
)
SELECT
    d.id,
    ov.id,
    nv.id,
    oc.id,
    NULL,
    'Removed',
    'Neutral',
    0.300,
    'Legacy postal/fax opt-out notice removed in favor of online privacy dashboard controls.',
    CURRENT_TIMESTAMP - INTERVAL '5 days'
FROM documents d
JOIN policy_versions ov ON ov.document_id = d.id AND ov.version_number = 'v1.0'
JOIN policy_versions nv ON nv.document_id = d.id AND nv.version_number = 'v2.0'
JOIN clauses oc ON oc.document_id = d.id AND oc.clause_title = 'Legacy Regional Opt-Out Fax Notice (Removed v1.0 Demo)'
WHERE d.document_name = '[DEMO] Google Privacy Policy (Illustrative Sample)'
  AND NOT EXISTS (
      SELECT 1 FROM policy_changes pc
      WHERE pc.old_version_id = ov.id AND pc.new_version_id = nv.id AND pc.change_type = 'Removed'
  );

-- Added clause: Immediate Price Notice Update on Amazon Demo v1.1
INSERT INTO policy_changes (
    document_id, old_version_id, new_version_id, old_clause_id, new_clause_id,
    change_type, change_direction, magnitude, change_summary, detected_at
)
SELECT
    d.id,
    ov.id,
    nv.id,
    NULL,
    nc.id,
    'Added',
    'Less Favorable',
    0.760,
    'Added clause allowing subscription price updates via electronic notice before the next billing cycle.',
    CURRENT_TIMESTAMP - INTERVAL '2 days'
FROM documents d
JOIN policy_versions ov ON ov.document_id = d.id AND ov.version_number = 'v1.0'
JOIN policy_versions nv ON nv.document_id = d.id AND nv.version_number = 'v1.1'
JOIN clauses nc ON nc.document_id = d.id AND nc.clause_title = 'Immediate Price Notice Update (Added v1.1 Demo)'
WHERE d.document_name = '[DEMO] Amazon Privacy Policy (Illustrative Sample)'
  AND NOT EXISTS (
      SELECT 1 FROM policy_changes pc
      WHERE pc.old_version_id = ov.id AND pc.new_version_id = nv.id AND pc.change_type = 'Added'
  );

-- -----------------------------------------------------------------------------
-- 4. Insert monitored_policies (Multiple users monitoring the same public doc!)
-- -----------------------------------------------------------------------------
INSERT INTO monitored_policies (
    user_id, document_id, policy_url, monitoring_status, check_interval_hours, last_checked_at, next_check_at
)
SELECT
    u.id,
    d.id,
    d.policy_url,
    v.monitoring_status,
    24,
    CURRENT_TIMESTAMP - INTERVAL '2 hours',
    CURRENT_TIMESTAMP + INTERVAL '22 hours'
FROM (
    VALUES
        ('alex_in',  '[DEMO] Google Privacy Policy (Illustrative Sample)', 'Active'),
        ('sarah_us', '[DEMO] Google Privacy Policy (Illustrative Sample)', 'Active'),
        ('sarah_us', '[DEMO] Amazon Privacy Policy (Illustrative Sample)', 'Active'),
        ('john_eu',  '[DEMO] Microsoft Services Agreement (Illustrative Sample)', 'Paused')
) AS v(username, document_name, monitoring_status)
JOIN users u ON u.username = v.username
JOIN documents d ON d.document_name = v.document_name
ON CONFLICT (user_id, document_id) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 5. Insert personalized notifications linked to policy_changes
-- -----------------------------------------------------------------------------
INSERT INTO notifications (
    user_id, policy_change_id, title, message, alert_score, severity, is_read
)
SELECT
    u.id,
    pc.id,
    '[DEMO ALERT] Google Privacy Policy Retention Period Increased',
    'Backup retention increased from 18 months to 36 months (Less Favorable). Relevant to your India Student profile.',
    0.810,
    'High',
    FALSE
FROM users u
JOIN documents d ON d.document_name = '[DEMO] Google Privacy Policy (Illustrative Sample)'
JOIN policy_changes pc ON pc.document_id = d.id AND pc.change_type = 'Modified'
WHERE u.username = 'alex_in'
ON CONFLICT (user_id, policy_change_id) WHERE policy_change_id IS NOT NULL DO NOTHING;

INSERT INTO notifications (
    user_id, policy_change_id, title, message, alert_score, severity, is_read
)
SELECT
    u.id,
    pc.id,
    '[DEMO ALERT] Subscription Price Notice Clause Added',
    'A new clause regarding automatic subscription price updates via electronic notice was added.',
    0.850,
    'Critical',
    FALSE
FROM users u
JOIN documents d ON d.document_name = '[DEMO] Amazon Privacy Policy (Illustrative Sample)'
JOIN policy_changes pc ON pc.document_id = d.id AND pc.change_type = 'Added'
WHERE u.username = 'sarah_us'
ON CONFLICT (user_id, policy_change_id) WHERE policy_change_id IS NOT NULL DO NOTHING;

COMMIT;
