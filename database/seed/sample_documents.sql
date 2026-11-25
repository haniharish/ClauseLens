-- =============================================================================
-- ClauseLens Demonstration Seed Data - seed/sample_documents.sql
-- NOTICE: Fictional/illustrative demonstration records only.
--         These entries simulate public legal policy metadata for academic demo
--         purposes and do NOT represent live legal findings or audits of the
--         named organizations.
-- =============================================================================

BEGIN;

INSERT INTO documents (
    user_id,
    document_name,
    document_type,
    file_path,
    policy_url,
    source_type,
    processing_status,
    is_public_policy
)
SELECT
    u.id,
    v.document_name,
    v.document_type,
    v.file_path,
    v.policy_url,
    v.source_type,
    v.processing_status,
    v.is_public_policy
FROM (
    VALUES
        (
            'alex_in',
            '[DEMO] Google Privacy Policy (Illustrative Sample)',
            'Privacy Policy',
            NULL,
            'https://policies.google.com/privacy',
            'URL',
            'Completed',
            TRUE
        ),
        (
            'sarah_us',
            '[DEMO] Instagram Terms and Conditions (Illustrative Sample)',
            'Terms and Conditions',
            'uploads/demo/instagram_terms_sample.pdf',
            'https://help.instagram.com/581066165581870',
            'PDF Upload',
            'Completed',
            TRUE
        ),
        (
            'sarah_us',
            '[DEMO] Amazon Privacy Policy (Illustrative Sample)',
            'Privacy Policy',
            NULL,
            'https://www.amazon.com/gp/help/customer/display.html?nodeId=GX7NJQ4ZB8MHFRNJ',
            'URL',
            'Completed',
            TRUE
        ),
        (
            'john_eu',
            '[DEMO] Microsoft Services Agreement (Illustrative Sample)',
            'Terms and Conditions',
            'uploads/demo/microsoft_services_agreement_sample.pdf',
            'https://www.microsoft.com/en-us/servicesagreement',
            'PDF Upload',
            'Completed',
            TRUE
        )
) AS v(owner_username, document_name, document_type, file_path, policy_url, source_type, processing_status, is_public_policy)
JOIN users u ON u.username = v.owner_username
WHERE NOT EXISTS (
    SELECT 1 FROM documents d WHERE d.document_name = v.document_name
);

COMMIT;
