-- =============================================================================
-- ClauseLens Demonstration Seed Data - seed/sample_clauses.sql
-- NOTICE: Fictional/illustrative clause excerpts, summaries, and risk scores
--         for ClauseLens academic demonstration. Not real legal findings.
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- 1. Insert illustrative clauses across the 4 demo documents
-- -----------------------------------------------------------------------------
INSERT INTO clauses (
    document_id, category_id, clause_title, original_text, severity_score, clause_order
)
SELECT
    d.id,
    cc.id,
    v.clause_title,
    v.original_text,
    v.severity_score,
    v.clause_order
FROM (
    VALUES
        -- Google Privacy Policy (Demo)
        (
            '[DEMO] Google Privacy Policy (Illustrative Sample)',
            'data_sharing',
            'Third-Party Partner & Advertising Data Sharing (Demo)',
            'ILLUSTRATIVE DEMO TEXT: We may share aggregated, pseudonymous, or device-linked telemetry with advertising networks, analytics vendors, and affiliated service partners to measure campaign performance and personalize content.',
            0.780,
            1
        ),
        (
            '[DEMO] Google Privacy Policy (Illustrative Sample)',
            'data_retention',
            'Extended Operational & Backup Data Retention (Demo)',
            'ILLUSTRATIVE DEMO TEXT: Certain activity logs and diagnostic metadata may be retained in encrypted archival backups for up to 36 months after account deletion to fulfill fraud-prevention and statutory audit obligations.',
            0.660,
            2
        ),
        -- Instagram Terms and Conditions (Demo)
        (
            '[DEMO] Instagram Terms and Conditions (Illustrative Sample)',
            'children_age',
            'Minor Eligibility & Youth Data Profiling (Demo)',
            'ILLUSTRATIVE DEMO TEXT: Users under the statutory age threshold must obtain verifiable guardian permission; however, engagement signals from teen accounts may still inform safety models and non-targeted feed ranking.',
            0.890,
            1
        ),
        (
            '[DEMO] Instagram Terms and Conditions (Illustrative Sample)',
            'account_termination',
            'Discretionary Account Suspension & Content Removal (Demo)',
            'ILLUSTRATIVE DEMO TEXT: We reserve the right to suspend or permanently disable access to your account without prior notice if we determine, in our sole discretion, that your conduct creates risk or violates community standards.',
            0.740,
            2
        ),
        -- Amazon Privacy Policy (Demo)
        (
            '[DEMO] Amazon Privacy Policy (Illustrative Sample)',
            'auto_renewal_fees',
            'Automatic Membership Renewal & Fee Adjustments (Demo)',
            'ILLUSTRATIVE DEMO TEXT: Subscription memberships automatically renew at the then-current standard rate unless canceled at least 24 hours before the end of the billing cycle; partial-month refunds are not guaranteed.',
            0.820,
            1
        ),
        (
            '[DEMO] Amazon Privacy Policy (Illustrative Sample)',
            'data_sharing',
            'Marketplace Seller & Affiliate Data Disclosure (Demo)',
            'ILLUSTRATIVE DEMO TEXT: Order fulfillment details, shipping addresses, and interaction records may be shared with independent marketplace merchants and third-party logistics providers handling your transactions.',
            0.710,
            2
        ),
        -- Microsoft Services Agreement (Demo)
        (
            '[DEMO] Microsoft Services Agreement (Illustrative Sample)',
            'arbitration_jurisdiction',
            'Binding Individual Arbitration & Class-Action Waiver (Demo)',
            'ILLUSTRATIVE DEMO TEXT: Any dispute arising out of these Terms shall be resolved exclusively through binding individual arbitration, and you waive the right to participate in class-action lawsuits or jury trials where permitted by law.',
            0.860,
            1
        ),
        (
            '[DEMO] Microsoft Services Agreement (Illustrative Sample)',
            'content_license',
            'Worldwide Operational License Over User Content (Demo)',
            'ILLUSTRATIVE DEMO TEXT: To operate and improve the services, you grant us a worldwide, royalty-free license to host, reproduce, cache, and transmit content you upload, subject to applicable statutory rights.',
            0.690,
            2
        )
) AS v(document_name, category_code, clause_title, original_text, severity_score, clause_order)
JOIN documents d ON d.document_name = v.document_name
JOIN clause_categories cc ON cc.code = v.category_code
ON CONFLICT (document_id, clause_order) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 2. Insert AI-generated plain-language summaries (strictly separate table)
-- -----------------------------------------------------------------------------
INSERT INTO clause_summaries (
    clause_id, simple_explanation, summary_language, model_name, summary_version
)
SELECT
    c.id,
    v.simple_explanation,
    'en',
    'clauselens-summarizer-demo-v1',
    1
FROM (
    VALUES
        (
            'Third-Party Partner & Advertising Data Sharing (Demo)',
            'Your usage and device identifiers may be shared with external ad and analytics partners for measurement and targeting.'
        ),
        (
            'Extended Operational & Backup Data Retention (Demo)',
            'Even after deleting your account, backup logs can remain stored for up to 3 years for security and compliance checks.'
        ),
        (
            'Minor Eligibility & Youth Data Profiling (Demo)',
            'Accounts used by minors require parental approval in regulated regions, and engagement signals may still shape platform feeds.'
        ),
        (
            'Discretionary Account Suspension & Content Removal (Demo)',
            'The platform can suspend or terminate your account immediately without advance warning if it flags a policy violation.'
        ),
        (
            'Automatic Membership Renewal & Fee Adjustments (Demo)',
            'Your paid subscription renews automatically at updated prices unless you cancel at least 24 hours before renewal.'
        ),
        (
            'Marketplace Seller & Affiliate Data Disclosure (Demo)',
            'Your shipping and order information is passed to third-party sellers and delivery partners fulfilling your purchase.'
        ),
        (
            'Binding Individual Arbitration & Class-Action Waiver (Demo)',
            'Disputes must go through private arbitration rather than court, though EU statutory consumer protections may override this.'
        ),
        (
            'Worldwide Operational License Over User Content (Demo)',
            'The provider receives a broad royalty-free license to host, copy, and transmit your uploaded files to run the service.'
        )
) AS v(clause_title, simple_explanation)
JOIN clauses c ON c.clause_title = v.clause_title
ON CONFLICT (clause_id, summary_language, model_name, summary_version) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 3. Insert aggregate analysis results (one latest completed result per doc)
-- -----------------------------------------------------------------------------
INSERT INTO analysis_results (
    document_id, total_clauses, high_risk_count, medium_risk_count, low_risk_count, overall_risk_score, analysis_status
)
SELECT
    d.id,
    COUNT(c.id)::INTEGER,
    COUNT(*) FILTER (WHERE c.severity_score >= 0.750)::INTEGER,
    COUNT(*) FILTER (WHERE c.severity_score >= 0.450 AND c.severity_score < 0.750)::INTEGER,
    COUNT(*) FILTER (WHERE c.severity_score < 0.450)::INTEGER,
    ROUND(AVG(c.severity_score) * 100.0, 2),
    'Completed'
FROM documents d
JOIN clauses c ON c.document_id = d.id
WHERE d.document_name LIKE '[DEMO]%'
  AND NOT EXISTS (
      SELECT 1 FROM analysis_results ar WHERE ar.document_id = d.id
  )
GROUP BY d.id;

-- -----------------------------------------------------------------------------
-- 4. Insert personalized risk assessments for Alex (India Student),
--    Sarah (USA Parent), and John (EU Freelancer)
-- -----------------------------------------------------------------------------
INSERT INTO personalized_risks (user_id, clause_id, relevance_score, risk_level, why_it_matters)
SELECT
    u.id,
    c.id,
    v.relevance_score,
    v.risk_level,
    v.why_it_matters
FROM (
    VALUES
        (
            'alex_in',
            'Third-Party Partner & Advertising Data Sharing (Demo)',
            0.840,
            'High',
            'As a student user in India, cross-partner ad sharing requires explicit notice and consent under India''s DPDP Act.'
        ),
        (
            'alex_in',
            'Discretionary Account Suspension & Content Removal (Demo)',
            0.790,
            'High',
            'Sudden account suspension can lock you out of academic resources or student-verified social access without appeal.'
        ),
        (
            'sarah_us',
            'Minor Eligibility & Youth Data Profiling (Demo)',
            0.950,
            'Critical',
            'As a Parent of a Minor in the United States, COPPA and state youth-privacy laws restrict behavioral profiling of children.'
        ),
        (
            'sarah_us',
            'Automatic Membership Renewal & Fee Adjustments (Demo)',
            0.860,
            'High',
            'Recurring household subscription charges can increase automatically without explicit re-confirmation.'
        ),
        (
            'john_eu',
            'Binding Individual Arbitration & Class-Action Waiver (Demo)',
            0.720,
            'High',
            'As an EU Freelancer/Business user, verify whether B2B terms override mandatory EU consumer court protections.'
        ),
        (
            'john_eu',
            'Worldwide Operational License Over User Content (Demo)',
            0.880,
            'Critical',
            'As a Freelancer uploading client deliverables, broad content licenses may conflict with client NDA or IP exclusivity.'
        )
) AS v(username, clause_title, relevance_score, risk_level, why_it_matters)
JOIN users u ON u.username = v.username
JOIN clauses c ON c.clause_title = v.clause_title
ON CONFLICT (user_id, clause_id) DO NOTHING;

COMMIT;
