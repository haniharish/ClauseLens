-- =============================================================================
-- ClauseLens Demonstration Seed Data - seed/sample_users.sql
-- NOTICE: Fictional/illustrative demonstration records only.
--         Passwords below are synthetic Django PBKDF2 placeholder hashes for
--         local testing only and must NEVER be used in production.
-- =============================================================================

BEGIN;

-- 1. Insert demonstration users
INSERT INTO users (username, full_name, email, password, is_active, is_staff, is_superuser)
VALUES
    (
        'alex_in',
        'Alex Verma',
        'alex.demo@clauselens.local',
        'pbkdf2_sha256$720000$demoSaltAlex01$9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
        TRUE, FALSE, FALSE
    ),
    (
        'sarah_us',
        'Sarah Jenkins',
        'sarah.demo@clauselens.local',
        'pbkdf2_sha256$720000$demoSaltSarah2$4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a',
        TRUE, FALSE, FALSE
    ),
    (
        'john_eu',
        'John Lindqvist',
        'john.demo@clauselens.local',
        'pbkdf2_sha256$720000$demoSaltJohn03$e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        TRUE, FALSE, FALSE
    )
ON CONFLICT (username) DO NOTHING;

-- 2. Insert 1:1 user profiles (Alex: Student in India, Sarah: Parent in USA, John: Freelancer in EU)
INSERT INTO user_profiles (user_id, age_group_id, jurisdiction_id)
SELECT
    u.id,
    ag.id,
    j.id
FROM users u
CROSS JOIN age_groups ag
CROSS JOIN jurisdictions j
WHERE (u.username = 'alex_in'  AND ag.code = '18_64' AND j.code = 'IN')
   OR (u.username = 'sarah_us' AND ag.code = '18_64' AND j.code = 'US')
   OR (u.username = 'john_eu'  AND ag.code = '18_64' AND j.code = 'EU')
ON CONFLICT (user_id) DO NOTHING;

-- 3. Insert multi-value intended-use tags (3NF junction table)
INSERT INTO user_profile_intended_uses (user_profile_id, intended_use_id)
SELECT up.id, iuc.id
FROM user_profiles up
JOIN users u ON u.id = up.user_id
JOIN intended_use_categories iuc ON (
    (u.username = 'alex_in'  AND iuc.code IN ('student', 'personal'))
    OR (u.username = 'sarah_us' AND iuc.code IN ('parent_of_minor', 'personal'))
    OR (u.username = 'john_eu'  AND iuc.code IN ('freelancer', 'business'))
)
ON CONFLICT (user_profile_id, intended_use_id) DO NOTHING;

COMMIT;
