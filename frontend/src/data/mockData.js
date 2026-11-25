// Demonstration mock data for ClauseLens frontend preview.
// Designed to mirror the upcoming Django REST Framework + Hugging Face + Sentence Transformers API schema.

export const DEFAULT_USER_PROFILE = {
  id: 'usr_alex_01',
  fullName: 'Alex Sharma',
  email: 'alex.sharma@university.edu',
  avatarInitials: 'AS',
  ageGroup: '18–64',
  intendedUse: ['Personal', 'Student'],
  jurisdiction: 'India',
  profileStatus: 'Active',
  keepLocalOnly: true,
};

export const DASHBOARD_STATS = [
  {
    id: 'docs_analyzed',
    label: 'Documents Analyzed',
    value: 24,
    icon: 'FileText',
    trend: '+12% this month',
    trendPositive: true,
    accent: 'purple',
  },
  {
    id: 'high_risk',
    label: 'High Risk Clauses',
    value: 18,
    icon: 'ShieldAlert',
    trend: 'Requires attention',
    trendPositive: false,
    accent: 'red',
  },
  {
    id: 'policies_monitored',
    label: 'Policies Monitored',
    value: 8,
    icon: 'Eye',
    trend: 'Actively tracking',
    trendPositive: true,
    accent: 'cyan',
  },
  {
    id: 'policy_changes',
    label: 'Policy Changes Detected',
    value: 12,
    icon: 'GitCompareArrows',
    trend: '3 important changes',
    trendPositive: false,
    accent: 'orange',
  },
];

export const RISK_DISTRIBUTION_DATA = [
  { name: 'Data Sharing', value: 26, color: '#9B7AFF' },
  { name: 'Data Collection', value: 22, color: '#3B82F6' },
  { name: 'Arbitration', value: 18, color: '#EF4444' },
  { name: 'Auto-Renewal & Fees', value: 15, color: '#F59E0B' },
  { name: 'Account Termination', value: 11, color: '#06B6D4' },
  { name: 'Other Clauses', value: 8, color: '#6366F1' },
];

export const RISK_TREND_DATA = [
  { month: 'Jun', riskScore: 61, highRiskCount: 11 },
  { month: 'Jul', riskScore: 64, highRiskCount: 13 },
  { month: 'Aug', riskScore: 68, highRiskCount: 14 },
  { month: 'Sep', riskScore: 66, highRiskCount: 15 },
  { month: 'Oct', riskScore: 70, highRiskCount: 16 },
  { month: 'Nov', riskScore: 72, highRiskCount: 18 },
];

export const INITIAL_DOCUMENTS = [
  {
    id: 'doc-google-privacy',
    name: 'Google Privacy Policy',
    type: 'Privacy Policy',
    fileType: 'PDF',
    fileSize: '1.42 MB',
    dateAnalyzed: '2026-11-22',
    clausesFound: 42,
    riskScore: 76,
    riskLevel: 'High Risk',
    status: 'Completed',
    sourceUrl: 'https://policies.google.com/privacy',
    summaryCounts: { high: 6, medium: 19, low: 17 },
    clauses: [
      {
        id: 'gp-1',
        title: 'Third-Party Data Sharing & Subprocessors',
        originalText:
          'We may share personal information with companies, organizations, or individuals outside of Google for external processing, including trusted affiliates and service providers, subject to confidentiality obligations and applicable data transfer frameworks.',
        simpleExplanation:
          'Google can send your personal data to external partner companies and vendors that help operate its services, including across international borders.',
        category: 'Data Sharing',
        riskLevel: 'High',
        relevanceScore: 88,
        whyItMatters:
          'As a student in India using personal workspace and cloud accounts, your activity and metadata may be processed outside India by third-party vendors.',
        saved: true,
      },
      {
        id: 'gp-2',
        title: 'Cross-Service Behavioral Profiling',
        originalText:
          'We collect information about your activity across our services, including terms you search for, videos you watch, views and interactions with content and ads, and voice and audio information when you use audio features.',
        simpleExplanation:
          'Activity from Search, YouTube, Maps, and Chrome is combined into a unified behavioral profile used for personalization and ad targeting.',
        category: 'Data Collection',
        riskLevel: 'High',
        relevanceScore: 84,
        whyItMatters:
          'Your academic searches and personal browsing habits may be linked together under one advertising and personalization profile.',
        saved: false,
      },
      {
        id: 'gp-3',
        title: 'Extended Server Log & Backup Retention',
        originalText:
          'Even after you delete information from your account, residual copies may remain on active servers and backup systems for up to 180 days before permanent purge, or longer if required by legal preservation requests.',
        simpleExplanation:
          'Deleting files or history does not remove them immediately; backup copies can remain stored for up to 6 months.',
        category: 'Data Collection',
        riskLevel: 'Medium',
        relevanceScore: 73,
        whyItMatters:
          'If you remove sensitive project or personal data, copies persist in backup archives for several months.',
        saved: false,
      },
      {
        id: 'gp-4',
        title: 'Automated Content Scanning for Abuse & Security',
        originalText:
          'Our automated systems analyze your content (including emails and documents) to provide you personally relevant product features, detect spam and malware, and enforce platform integrity policies.',
        simpleExplanation:
          'Automated software scans uploaded documents and emails for security threats, spam, and smart features.',
        category: 'Other Clauses',
        riskLevel: 'Low',
        relevanceScore: 46,
        whyItMatters:
          'Standard automated scanning protects against malware, though you should still avoid uploading unencrypted confidential credentials.',
        saved: false,
      },
    ],
  },
  {
    id: 'doc-instagram-terms',
    name: 'Instagram Terms & Conditions',
    type: 'Terms & Conditions',
    fileType: 'URL',
    fileSize: '890 KB',
    dateAnalyzed: '2026-11-20',
    clausesFound: 36,
    riskScore: 84,
    riskLevel: 'High Risk',
    status: 'Completed',
    sourceUrl: 'https://help.instagram.com/581066165581870',
    summaryCounts: { high: 7, medium: 16, low: 13 },
    clauses: [
      {
        id: 'ig-1',
        title: 'Broad Perpetual License Over User Content',
        originalText:
          'You hereby grant to us a non-exclusive, royalty-free, transferable, sub-licensable, worldwide license to host, use, distribute, modify, run, copy, publicly perform or display, translate, and create derivative works of your content.',
        simpleExplanation:
          'By posting photos, reels, or captions, you allow Instagram and its partners to reuse, modify, and redistribute your content worldwide without paying you.',
        category: 'Data Sharing',
        riskLevel: 'High',
        relevanceScore: 91,
        whyItMatters:
          'Any portfolio work, creative designs, or personal videos you upload can be sublicensed or featured across Meta products without royalties.',
        saved: true,
      },
      {
        id: 'ig-2',
        title: 'Unilateral Account Suspension Without Prior Notice',
        originalText:
          'We can remove any content or information you share on the Service if we believe that it violates these Terms of Use, our policies, or we are permitted or required to do so by law, and may suspend or terminate access immediately.',
        simpleExplanation:
          'Instagram can lock or delete your account and content immediately based on its own moderation assessment without prior warning.',
        category: 'Account Termination',
        riskLevel: 'High',
        relevanceScore: 79,
        whyItMatters:
          'Accounts used for student clubs or side projects can lose followers and archived posts overnight with limited appeal options.',
        saved: false,
      },
      {
        id: 'ig-3',
        title: 'Mandatory Arbitration & Class Action Waiver (Select Regions)',
        originalText:
          'Except where prohibited by applicable statutory consumer protection law, disputes arising out of or relating to these Terms must be resolved through binding individual arbitration rather than jury trials or class actions.',
        simpleExplanation:
          'You generally give up the right to join group lawsuits and must resolve disputes individually in private arbitration where enforceable.',
        category: 'Arbitration',
        riskLevel: 'Medium',
        relevanceScore: 68,
        whyItMatters:
          'Although Indian consumer law provides certain non-waivable protections, cross-border platform disputes face high legal friction.',
        saved: false,
      },
    ],
  },
  {
    id: 'doc-amazon-privacy',
    name: 'Amazon Privacy Policy',
    type: 'Privacy Policy',
    fileType: 'PDF',
    fileSize: '1.18 MB',
    dateAnalyzed: '2026-11-18',
    clausesFound: 31,
    riskScore: 65,
    riskLevel: 'Medium Risk',
    status: 'Completed',
    sourceUrl: 'https://www.amazon.in/gp/help/customer/display.html',
    summaryCounts: { high: 3, medium: 15, low: 13 },
    clauses: [
      {
        id: 'az-1',
        title: 'Third-Party Marketplace Seller Data Disclosure',
        originalText:
          'When you purchase products offered by third-party sellers on Amazon marketplaces, we share transaction details, delivery addresses, and contact metadata necessary to fulfill orders and handle returns.',
        simpleExplanation:
          'Independent marketplace sellers receive your name, shipping address, and order details whenever you buy their items.',
        category: 'Data Sharing',
        riskLevel: 'Medium',
        relevanceScore: 74,
        whyItMatters:
          'Your residential or hostel address and phone number are shared directly with external merchants outside Amazon.',
        saved: false,
      },
      {
        id: 'az-2',
        title: 'Prime Membership Auto-Renewal Billing',
        originalText:
          'Unless you disable automatic renewal in your account settings prior to the end of the current billing period, your subscription will automatically renew at the then-current standard rate using your stored payment method.',
        simpleExplanation:
          'Your student or standard Prime plan renews automatically and charges your saved card or UPI mandate unless canceled beforehand.',
        category: 'Auto-Renewal & Fees',
        riskLevel: 'High',
        relevanceScore: 86,
        whyItMatters:
          'Discounted student trials convert to full-price recurring billing automatically if you forget to cancel before expiry.',
        saved: true,
      },
      {
        id: 'az-3',
        title: 'Voice Recordings & Device Telemetry',
        originalText:
          'Voice inputs processed through Alexa-enabled devices are transmitted to cloud servers to transcribe requests, improve speech recognition models, and deliver requested actions.',
        simpleExplanation:
          'Voice commands on smart devices are uploaded and analyzed in the cloud to improve recognition accuracy.',
        category: 'Data Collection',
        riskLevel: 'Medium',
        relevanceScore: 62,
        whyItMatters:
          'Voice clips may be retained for model training unless you manually opt out in privacy settings.',
        saved: false,
      },
    ],
  },
  {
    id: 'doc-linkedin-agreement',
    name: 'LinkedIn User Agreement',
    type: 'User Agreement',
    fileType: 'PDF',
    fileSize: '960 KB',
    dateAnalyzed: '2026-11-15',
    clausesFound: 28,
    riskScore: 58,
    riskLevel: 'Medium Risk',
    status: 'Completed',
    sourceUrl: 'https://www.linkedin.com/legal/user-agreement',
    summaryCounts: { high: 2, medium: 12, low: 14 },
    clauses: [
      {
        id: 'li-1',
        title: 'AI Model Training Opt-Out Default',
        originalText:
          'LinkedIn may use public profile information, posts, and engagement signals to train generative AI and matching algorithms unless the member adjusts data privacy toggles in account settings.',
        simpleExplanation:
          'Your resume details and posts can be used to train AI systems unless you manually turn off the setting.',
        category: 'Data Collection',
        riskLevel: 'Medium',
        relevanceScore: 77,
        whyItMatters:
          'As a student actively sharing resumes and projects, your career data feeds recommendation and AI models by default.',
        saved: false,
      },
      {
        id: 'li-2',
        title: 'Premium Subscription Renewal & Non-Refundable Partial Periods',
        originalText:
          'Paid subscriptions renew automatically on a monthly or annual cycle. Fees paid for the active billing period are generally non-refundable once the renewal date has passed.',
        simpleExplanation:
          'LinkedIn Premium renews automatically and does not usually refund the month if you cancel mid-cycle.',
        category: 'Auto-Renewal & Fees',
        riskLevel: 'Medium',
        relevanceScore: 71,
        whyItMatters:
          'Student career trials convert into paid plans unless canceled 24 hours before renewal.',
        saved: false,
      },
    ],
  },
  {
    id: 'doc-microsoft-services',
    name: 'Microsoft Services Agreement',
    type: 'Services Agreement',
    fileType: 'PDF',
    fileSize: '1.65 MB',
    dateAnalyzed: '2026-11-11',
    clausesFound: 24,
    riskScore: 39,
    riskLevel: 'Low Risk',
    status: 'Completed',
    sourceUrl: 'https://www.microsoft.com/en-in/servicesagreement',
    summaryCounts: { high: 0, medium: 8, low: 16 },
    clauses: [
      {
        id: 'ms-1',
        title: 'OneDrive Inactivity & Storage Quota Enforcement',
        originalText:
          'If your Microsoft account remains inactive for more than two consecutive years, or if you exceed allocated cloud storage limits for an extended period, Microsoft may freeze or delete stored files after advance notice.',
        simpleExplanation:
          'Inactive accounts (2+ years) or over-quota OneDrive storage may be frozen or purged after warning emails.',
        category: 'Account Termination',
        riskLevel: 'Low',
        relevanceScore: 52,
        whyItMatters:
          'Important for graduating students whose university-linked storage quotas may drop after graduation.',
        saved: false,
      },
      {
        id: 'ms-2',
        title: 'Regional Consumer Rights Preservation',
        originalText:
          'Nothing in this agreement limits mandatory statutory consumer protection rights granted under the laws of your country of residence.',
        simpleExplanation:
          'Local consumer protection laws in India still apply regardless of standard contract terms.',
        category: 'Other Clauses',
        riskLevel: 'Low',
        relevanceScore: 34,
        whyItMatters:
          'Positive protection ensuring Indian statutory consumer rights are not overridden.',
        saved: false,
      },
    ],
  },
];

export const INITIAL_POLICY_UPDATES = [
  {
    id: 'upd-1',
    documentId: 'doc-google-privacy',
    documentName: 'Google Privacy Policy',
    changeType: 'Modified',
    dateDetected: '2026-11-23',
    riskImpact: 'High',
    summary: 'Data retention clause modified.',
    detail: 'Potentially important change detected.',
    versionRef: 'ver-google-42',
  },
  {
    id: 'upd-2',
    documentId: 'doc-instagram-terms',
    documentName: 'Instagram Terms & Conditions',
    changeType: 'Added',
    dateDetected: '2026-11-20',
    riskImpact: 'High',
    summary: 'AI training & derivative content rights expanded.',
    detail: 'Impacts public posts and creator reels.',
    versionRef: 'ver-insta-26',
  },
  {
    id: 'upd-3',
    documentId: 'doc-amazon-privacy',
    documentName: 'Amazon Privacy Policy',
    changeType: 'Modified',
    dateDetected: '2026-11-17',
    riskImpact: 'Medium',
    summary: 'Third-party ad partner disclosure updated.',
    detail: 'Expanded list of measurement affiliates.',
    versionRef: 'ver-amazon-31',
  },
  {
    id: 'upd-4',
    documentId: 'doc-microsoft-services',
    documentName: 'Microsoft Services Agreement',
    changeType: 'Removed',
    dateDetected: '2026-11-12',
    riskImpact: 'Low',
    summary: 'Legacy Skype billing reference removed.',
    detail: 'Clarification with minimal user impact.',
    versionRef: 'ver-ms-25',
  },
];

export const INITIAL_MONITORED_POLICIES = [
  {
    id: 'mon-google',
    service: 'Google',
    policyName: 'Google Privacy Policy',
    url: 'https://policies.google.com/privacy',
    lastChecked: '2026-11-25 18:30',
    currentVersion: 'v4.2',
    status: 'Active',
    latestChange: 'Data retention window extended (Nov 23)',
    documentId: 'doc-google-privacy',
  },
  {
    id: 'mon-instagram',
    service: 'Instagram',
    policyName: 'Instagram Terms & Conditions',
    url: 'https://help.instagram.com/581066165581870',
    lastChecked: '2026-11-25 17:45',
    currentVersion: 'v2026.1',
    status: 'Active',
    latestChange: 'AI content license paragraph added (Nov 20)',
    documentId: 'doc-instagram-terms',
  },
  {
    id: 'mon-amazon',
    service: 'Amazon',
    policyName: 'Amazon Privacy Policy',
    url: 'https://www.amazon.in/gp/help/customer/display.html',
    lastChecked: '2026-11-25 14:15',
    currentVersion: 'v3.1',
    status: 'Active',
    latestChange: 'Ad partner telemetry wording revised (Nov 17)',
    documentId: 'doc-amazon-privacy',
  },
  {
    id: 'mon-microsoft',
    service: 'Microsoft',
    policyName: 'Microsoft Services Agreement',
    url: 'https://www.microsoft.com/en-in/servicesagreement',
    lastChecked: '2026-11-24 22:00',
    currentVersion: 'v2.5',
    status: 'Paused',
    latestChange: 'Legacy service clauses removed (Nov 12)',
    documentId: 'doc-microsoft-services',
  },
];

export const VERSION_COMPARISONS = [
  {
    id: 'ver-google-42',
    service: 'Google Privacy Policy',
    previousVersion: 'v4.1 (Oct 2026)',
    currentVersion: 'v4.2 (Nov 2026)',
    lastUpdated: '2026-11-23',
    changesDetected: 4,
    aiSummary:
      'The company has extended the data retention period for deleted account logs and backup archives from 30 days to 180 days, while broadening automated security scanning definitions.',
    changeDirection: 'Less favorable',
    impactLevel: 'High',
    personalizedAlertScore: 87,
    whyItMatters:
      'As a student in India, deleted search logs and cloud workspace metadata remain recoverable in backup storage six times longer than under the previous policy.',
    diffs: [
      {
        id: 'diff-1',
        section: 'Section 4.2 — Data Retention & Deletion',
        category: 'Modified',
        oldText:
          'When you delete personal activity from your account, we initiate deletion immediately and purge residual copies from backup systems within 30 days.',
        newText:
          'When you delete personal activity from your account, residual copies may remain on active servers and backup systems for up to 180 days before permanent purge.',
      },
      {
        id: 'diff-2',
        section: 'Section 5.1 — Third-Party AI Safety Processing',
        category: 'Added',
        oldText: '',
        newText:
          'De-identified interaction snippets may be evaluated by vetted safety reviewers and automated classifiers to mitigate abuse and improve generative model reliability.',
      },
      {
        id: 'diff-3',
        section: 'Section 6.4 — Legacy Workspace Export Notice',
        category: 'Removed',
        oldText:
          'Users will receive a 90-day SMS reminder prior to expiration of inactive archival exports.',
        newText: '',
      },
      {
        id: 'diff-4',
        section: 'Section 8.1 — Statutory Compliance',
        category: 'Unchanged',
        oldText:
          'We regularly review our compliance with regional privacy frameworks and respond to verified data access requests.',
        newText:
          'We regularly review our compliance with regional privacy frameworks and respond to verified data access requests.',
      },
    ],
  },
  {
    id: 'ver-insta-26',
    service: 'Instagram Terms & Conditions',
    previousVersion: 'v2025.3 (Aug 2025)',
    currentVersion: 'v2026.1 (Nov 2026)',
    lastUpdated: '2026-11-20',
    changesDetected: 3,
    aiSummary:
      'Instagram added explicit language permitting public posts, captions, and reels to be used for generative AI feature development, alongside clearer appeal windows for account suspensions.',
    changeDirection: 'Less favorable',
    impactLevel: 'High',
    personalizedAlertScore: 91,
    whyItMatters:
      'Public student portfolios, photography, and captions posted on public accounts may be ingested into generative AI training pipelines unless set to private.',
    diffs: [
      {
        id: 'ig-diff-1',
        section: 'Section 3.3 — Content License & AI Systems',
        category: 'Added',
        oldText: '',
        newText:
          'Your public content, including captions, images, and audio interactions, may be used to train and evaluate Meta AI models and recommendation features.',
      },
      {
        id: 'ig-diff-2',
        section: 'Section 7.2 — Account Suspension Appeals',
        category: 'Modified',
        oldText:
          'Disabled accounts may be reviewed upon written request without a defined response timeframe.',
        newText:
          'Disabled accounts may submit an in-app appeal within 180 days of suspension, with automated triage followed by human review for eligible cases.',
      },
      {
        id: 'ig-diff-3',
        section: 'Section 9.1 — Age Eligibility',
        category: 'Unchanged',
        oldText:
          'You must be at least 13 years old (or the minimum legal age in your country) to use Instagram.',
        newText:
          'You must be at least 13 years old (or the minimum legal age in your country) to use Instagram.',
      },
    ],
  },
  {
    id: 'ver-amazon-31',
    service: 'Amazon Privacy Policy',
    previousVersion: 'v3.0 (May 2026)',
    currentVersion: 'v3.1 (Nov 2026)',
    lastUpdated: '2026-11-17',
    changesDetected: 2,
    aiSummary:
      'Updated disclosures clarify how ad measurement partners receive aggregated conversion metrics and provide an explicit link to manage UPI AutoPay mandates.',
    changeDirection: 'Neutral',
    impactLevel: 'Medium',
    personalizedAlertScore: 64,
    whyItMatters:
      'Improves transparency for managing recurring Prime billing mandates in India, though ad-measurement data sharing remains active by default.',
    diffs: [
      {
        id: 'az-diff-1',
        section: 'Section 2.4 — Ad Measurement Partners',
        category: 'Modified',
        oldText:
          'We share limited campaign metrics with advertising partners.',
        newText:
          'We share aggregated conversion events and pseudonymized device identifiers with accredited ad measurement partners.',
      },
      {
        id: 'az-diff-2',
        section: 'Section 6.2 — Recurring Payment Controls',
        category: 'Added',
        oldText: '',
        newText:
          'Customers in India may pause or revoke recurring UPI AutoPay mandates directly from the Your Memberships & Subscriptions dashboard.',
      },
    ],
  },
];

export const INITIAL_NOTIFICATIONS = [
  {
    id: 'notif-1',
    title: 'Critical Policy Update: Google Privacy Policy',
    description:
      'Data retention period for deleted account logs extended from 30 days to 180 days (Relevance Score: 87/100).',
    timestamp: '2026-11-25 18:15',
    severity: 'critical',
    category: 'Policy Update',
    read: false,
    link: '/version-history?id=ver-google-42',
  },
  {
    id: 'notif-2',
    title: 'High-Risk Clause Alert: Instagram Terms & Conditions',
    description:
      'New clause grants broad AI training and derivative rights over public user content.',
    timestamp: '2026-11-24 14:40',
    severity: 'critical',
    category: 'High-Risk Clause',
    read: false,
    link: '/analysis/doc-instagram-terms',
  },
  {
    id: 'notif-3',
    title: 'Modified Clause Detected: Amazon Privacy Policy',
    description:
      'Ad measurement partner telemetry wording was updated in v3.1.',
    timestamp: '2026-11-22 10:12',
    severity: 'warning',
    category: 'Modified Clause',
    read: false,
    link: '/version-history?id=ver-amazon-31',
  },
  {
    id: 'notif-4',
    title: 'Document Analysis Completed: LinkedIn User Agreement',
    description:
      '28 clauses extracted and personalized for your Student (India) profile. Overall Risk: 58/100.',
    timestamp: '2026-11-15 16:05',
    severity: 'info',
    category: 'Analysis Completed',
    read: true,
    link: '/analysis/doc-linkedin-agreement',
  },
  {
    id: 'notif-5',
    title: 'Removed Clause: Microsoft Services Agreement',
    description:
      'Legacy Skype billing terms were removed in v2.5 with low risk impact.',
    timestamp: '2026-11-12 09:30',
    severity: 'info',
    category: 'Removed Clause',
    read: true,
    link: '/documents',
  },
];

export const PERSONA_COMPARISON_DATA = [
  {
    persona: 'Students',
    topCategories: ['Data Collection', 'Auto-Renewal & Fees', 'Data Sharing'],
    avgRelevance: 82,
    keyConcern:
      'Student trial auto-renewals, educational/personal data profiling across devices, and portfolio IP licensing.',
    exampleClause: 'Prime / SaaS trial converts automatically to annual billing; public posts licensed for AI training.',
    color: '#9B7AFF',
  },
  {
    persona: 'Parents',
    topCategories: ['Data Collection', 'Data Sharing', 'Account Termination'],
    avgRelevance: 90,
    keyConcern:
      'Minor data collection, voice/location telemetry, targeted advertising to under-18 accounts, and parental consent verification.',
    exampleClause: 'Behavioral tracking and voice recordings collected unless parental privacy controls are manually enabled.',
    color: '#06B6D4',
  },
  {
    persona: 'Freelancers',
    topCategories: ['Auto-Renewal & Fees', 'Arbitration', 'Account Termination'],
    avgRelevance: 85,
    keyConcern:
      'Unilateral account freezes cutting off client access, non-refundable subscription locks, and broad content sub-licensing.',
    exampleClause: 'Platform may suspend account immediately without prior notice and retain non-refundable annual fees.',
    color: '#F59E0B',
  },
  {
    persona: 'Business Owners',
    topCategories: ['Arbitration', 'Data Sharing', 'Data Collection'],
    avgRelevance: 88,
    keyConcern:
      'Cross-border subprocessor transfers, mandatory individual arbitration clauses, and liability caps on commercial data loss.',
    exampleClause: 'Disputes must be settled via binding individual arbitration; liability capped at 12 months of fees.',
    color: '#EF4444',
  },
];
