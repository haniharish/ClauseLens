"""
ClauseLens – Version Tracking Service Client.

This module is the ONLY place in the backend that calls Member 6's
version tracking / web crawler service.

The backend does NOT implement web crawling itself.

Contract with Member 6 (Version Tracking module):
  GET {VERSION_SERVICE_URL}/check/?url=<policy_url>&document_id=<id>
  Headers: X-Internal-Token: <token>

  Returns:
  {
      "document_id": int,
      "version_number": int,
      "version_text": str,
      "content_hash": str,
      "has_changes": bool,
      "changes": [
          {
              "clause_id": int|null,
              "new_clause_title": str,
              "new_clause_text": str,
              "change_type": "added"|"removed"|"modified"|"unchanged",
              "change_direction": "more_favorable"|"neutral"|"less_favorable"|"unclear",
              "magnitude": float
          }
      ]
  }

  Member 6 can also PUSH updates directly to:
  POST /api/internal/version-update/
  (Protected by X-Internal-Token)
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger('clauselens')

REQUEST_TIMEOUT = 30


class VersionServiceUnavailable(Exception):
    pass


class RealVersionClient:
    """HTTP client for Member 6's version tracking service."""

    def __init__(self):
        self.base_url = settings.VERSION_SERVICE_URL
        self.token = settings.INTERNAL_SERVICE_TOKEN

    def check_for_updates(self, document_id: int, policy_url: str) -> dict:
        url = f'{self.base_url}/check/'
        params = {'url': policy_url, 'document_id': document_id}
        headers = {'X-Internal-Token': self.token}
        try:
            response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as exc:
            raise VersionServiceUnavailable('Version service unreachable.') from exc
        except requests.exceptions.Timeout as exc:
            raise VersionServiceUnavailable('Version service timed out.') from exc
        except requests.exceptions.HTTPError as exc:
            raise VersionServiceUnavailable(f'Version service error: {exc}') from exc


class MockVersionClient:
    """Mock version client – returns empty 'no changes' response."""

    def check_for_updates(self, document_id: int, policy_url: str) -> dict:
        logger.warning('[MOCK] Version check – returning no changes.')
        return {
            'document_id': document_id,
            'version_number': 1,
            'version_text': '[MOCK version text]',
            'content_hash': 'mock_hash_000',
            'has_changes': False,
            'changes': [],
        }


def get_version_client():
    if getattr(settings, 'USE_MOCK_VERSION', True):
        return MockVersionClient()
    return RealVersionClient()
