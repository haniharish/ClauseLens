import api, { USE_MOCK_API } from './api';
import { INITIAL_DOCUMENTS, INITIAL_MONITORED_POLICIES } from '../data/mockData';
import { formatFileSize } from '../utils/helpers';

export const documentService = {
  async getDocuments() {
    if (USE_MOCK_API) {
      return INITIAL_DOCUMENTS;
    }
    const { data } = await api.get('/documents/');
    return data;
  },

  async getDocumentById(id) {
    if (USE_MOCK_API) {
      return INITIAL_DOCUMENTS.find((doc) => doc.id === id) || INITIAL_DOCUMENTS[0];
    }
    const { data } = await api.get(`/documents/${id}/`);
    return data;
  },

  async uploadAndAnalyze({ file, policyUrl, docType }) {
    if (USE_MOCK_API) {
      const nameFromFile = file ? file.name.replace(/\.pdf$/i, '') : null;
      let nameFromUrl = 'Custom Website Policy';
      if (policyUrl) {
        try {
          const parsed = new URL(policyUrl);
          nameFromUrl = `${parsed.hostname.replace(/^www\./, '')} Policy`;
        } catch {
          nameFromUrl = policyUrl.slice(0, 32);
        }
      }
      const newDoc = {
        id: `doc-${Date.now()}`,
        name: nameFromFile || nameFromUrl,
        type: docType || 'Terms & Conditions',
        fileType: file ? 'PDF' : 'URL',
        fileSize: file ? formatFileSize(file.size) : '420 KB',
        dateAnalyzed: new Date().toISOString().split('T')[0],
        clausesFound: 14,
        riskScore: 74,
        riskLevel: 'High Risk',
        status: 'Completed',
        sourceUrl: policyUrl || '',
        summaryCounts: { high: 3, medium: 6, low: 5 },
        clauses: [
          {
            id: `c-${Date.now()}-1`,
            title: 'Third-Party Data Sharing',
            originalText:
              'The company may share personal information with third-party service providers, analytics partners, and corporate affiliates to deliver and personalize the service.',
            simpleExplanation:
              'The company can share your personal information with other organizations that provide services to it or help run analytics.',
            category: 'Data Sharing',
            riskLevel: 'High',
            relevanceScore: 85,
            whyItMatters:
              'As a student using this platform for personal purposes, your information may be shared with external service providers.',
            saved: false,
          },
          {
            id: `c-${Date.now()}-2`,
            title: 'Automatic Subscription Renewal',
            originalText:
              'Paid plans automatically renew at the end of each billing cycle at the standard non-promotional rate unless canceled at least 24 hours prior to renewal.',
            simpleExplanation:
              'Your subscription automatically renews and charges full price unless you cancel at least one day before the billing date.',
            category: 'Auto-Renewal & Fees',
            riskLevel: 'High',
            relevanceScore: 82,
            whyItMatters:
              'Promotional or student discounts expire on renewal, resulting in higher recurring charges.',
            saved: false,
          },
          {
            id: `c-${Date.now()}-3`,
            title: 'Binding Individual Arbitration',
            originalText:
              'Any claim or dispute shall be resolved exclusively through final and binding individual arbitration, waiving the right to participate in class-action proceedings.',
            simpleExplanation:
              'Legal disputes must go through private individual arbitration rather than standard court or group lawsuits.',
            category: 'Arbitration',
            riskLevel: 'Medium',
            relevanceScore: 67,
            whyItMatters:
              'Limits collective legal remedies if a broad billing or data issue affects multiple users.',
            saved: false,
          },
          {
            id: `c-${Date.now()}-4`,
            title: 'Account Termination for Inactivity',
            originalText:
              'We reserve the right to suspend or terminate accounts that remain inactive for more than 12 consecutive months upon prior email notification.',
            simpleExplanation:
              'If you do not sign in for a year, the service can close your account after emailing you.',
            category: 'Account Termination',
            riskLevel: 'Low',
            relevanceScore: 41,
            whyItMatters:
              'Low immediate risk, though saved project files should be backed up periodically.',
            saved: false,
          },
        ],
      };
      return newDoc;
    }

    const formData = new FormData();
    if (file) formData.append('file', file);
    if (policyUrl) formData.append('policy_url', policyUrl);
    if (docType) formData.append('document_type', docType);
    const { data } = await api.post('/documents/analyze/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async deleteDocument(id) {
    if (USE_MOCK_API) return { deleted: id };
    const { data } = await api.delete(`/documents/${id}/`);
    return data;
  },

  async getMonitoredPolicies() {
    if (USE_MOCK_API) return INITIAL_MONITORED_POLICIES;
    const { data } = await api.get('/monitoring/');
    return data;
  },

  async addMonitoredPolicy(payload) {
    if (USE_MOCK_API) {
      return {
        id: `mon-${Date.now()}`,
        service: payload.service,
        policyName: payload.policyName,
        url: payload.url,
        lastChecked: 'Just now',
        currentVersion: 'v1.0 (Baseline)',
        status: 'Active',
        latestChange: 'Baseline snapshot captured (Demo)',
        documentId: 'doc-google-privacy',
      };
    }
    const { data } = await api.post('/monitoring/', payload);
    return data;
  },
};
