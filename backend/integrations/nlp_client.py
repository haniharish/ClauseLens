"""
ClauseLens – NLP Service Client.

This module is the ONLY place in the backend that calls Member 4's NLP service.
It provides:
  - A real HTTP client (RealNLPClient) that calls the NLP service.
  - A mock adapter (MockNLPClient) for local testing without the real service.
  - A factory function get_nlp_client() that picks the right one based on settings.

Contract with Member 4 (NLP module):
  POST {NLP_SERVICE_URL}/analyze/
  Headers: X-Internal-Token: <token>
  Body:    { "document_id": int, "document_url": str|null, "file_path": str|null }
  Returns: {
      "document_id": int,
      "total_clauses": int,
      "clauses": [
          {
              "clause_title": str,
              "original_text": str,
              "category": str,   # see Clause.Category choices
              "severity": float, # 0.0 – 1.0
              "simple_explanation": str
          }, ...
      ]
  }
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger('clauselens')

REQUEST_TIMEOUT = 30  # seconds


class NLPServiceUnavailable(Exception):
    """Raised when the NLP service cannot be reached."""


class RealNLPClient:
    """HTTP client that calls the real NLP microservice (Member 4)."""

    def __init__(self):
        self.base_url = settings.NLP_SERVICE_URL
        self.token = settings.INTERNAL_SERVICE_TOKEN

    def analyze_document(self, document_id: int, document) -> dict:
        """
        Send a document for NLP analysis and return the structured result.
        :param document_id: DB primary key of the document.
        :param document:    Document model instance.
        :raises NLPServiceUnavailable: if the service is down.
        """
        url = f'{self.base_url}/analyze/'
        payload = {
            'document_id': document_id,
            'document_url': document.policy_url,
            'file_path': document.file.name if document.file else None,
        }
        headers = {'X-Internal-Token': self.token}

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as exc:
            logger.error('NLP service unreachable: %s', exc)
            raise NLPServiceUnavailable('NLP service is unreachable.') from exc
        except requests.exceptions.Timeout as exc:
            logger.error('NLP service timed out.')
            raise NLPServiceUnavailable('NLP service request timed out.') from exc
        except requests.exceptions.HTTPError as exc:
            logger.error('NLP service returned error: %s', exc)
            raise NLPServiceUnavailable(f'NLP service error: {exc}') from exc


class MockNLPClient:
    """
    Mock NLP client for local development and testing.
    Returns synthetic clause data so the backend can be tested
    without Member 4's service running.
    """

    def analyze_document(self, document_id: int, document) -> dict:
        logger.warning(
            '[MOCK] NLP analysis for document %d – using mock data.', document_id
        )
        return {
            'document_id': document_id,
            'total_clauses': 3,
            'clauses': [
                {
                    'clause_title': 'Third Party Data Sharing [MOCK]',
                    'original_text': 'The company may share your personal data with third parties.',
                    'category': 'data_sharing',
                    'severity': 0.85,
                    'simple_explanation': 'Your data may be shared with other organisations.',
                },
                {
                    'clause_title': 'Automatic Renewal [MOCK]',
                    'original_text': 'Your subscription will automatically renew each year.',
                    'category': 'auto_renewal',
                    'severity': 0.60,
                    'simple_explanation': 'You will be charged again unless you cancel.',
                },
                {
                    'clause_title': 'Data Retention [MOCK]',
                    'original_text': 'We retain data for up to 5 years after account closure.',
                    'category': 'data_retention',
                    'severity': 0.40,
                    'simple_explanation': 'Your data is kept for five years after you leave.',
                },
            ],
        }


def get_nlp_client():
    """
    Factory: return the appropriate NLP client based on settings.
    Set USE_MOCK_NLP=True in .env to use the mock during development.
    """
    if getattr(settings, 'USE_MOCK_NLP', True):
        return MockNLPClient()
    return RealNLPClient()
