"""
ClauseLens – Personalization Service Client.

This module is the ONLY place in the backend that calls Member 5's
personalization/risk-scoring service.

Contract with Member 5 (Personalization module):
  POST {PERSONALIZATION_SERVICE_URL}/score/
  Headers: X-Internal-Token: <token>
  Body:
  {
      "user_id": int,
      "age_group": str,
      "intended_use": [str],
      "jurisdiction": str,
      "clauses": [
          {
              "clause_id": int,
              "category": str,
              "severity": float,
              "original_text": str
          }, ...
      ]
  }

  Returns:
  {
      "user_id": int,
      "results": [
          {
              "clause_id": int,
              "relevance_score": float,  # R(c,u) = S(c)[λ·cos + (1-λ)·L]
              "risk_level": "High"|"Medium"|"Low",
              "why_it_matters": str
          }, ...
      ]
  }
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger('clauselens')

REQUEST_TIMEOUT = 30


class PersonalizationServiceUnavailable(Exception):
    """Raised when the personalization service cannot be reached."""


class RealPersonalizationClient:
    """HTTP client for Member 5's personalization service."""

    def __init__(self):
        self.base_url = settings.PERSONALIZATION_SERVICE_URL
        self.token = settings.INTERNAL_SERVICE_TOKEN

    def score_clauses(self, user, profile, clauses) -> dict:
        url = f'{self.base_url}/score/'
        payload = {
            'user_id': user.id,
            'age_group': profile.age_group if profile else 'adult',
            'intended_use': profile.get_intended_use_list() if profile else ['personal'],
            'jurisdiction': profile.jurisdiction if profile else 'other',
            'clauses': [
                {
                    'clause_id': c.id,
                    'category': c.category,
                    'severity': c.severity,
                    'original_text': c.original_text,
                }
                for c in clauses
            ],
        }
        headers = {'X-Internal-Token': self.token}
        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as exc:
            raise PersonalizationServiceUnavailable('Personalization service unreachable.') from exc
        except requests.exceptions.Timeout as exc:
            raise PersonalizationServiceUnavailable('Personalization service timed out.') from exc
        except requests.exceptions.HTTPError as exc:
            raise PersonalizationServiceUnavailable(f'Personalization error: {exc}') from exc


class MockPersonalizationClient:
    """
    Mock personalization client.
    Uses a simplified version of the formula:
      R = S(c) × 0.7  (placeholder until Member 5's service is running)
    """

    def score_clauses(self, user, profile, clauses) -> dict:
        logger.warning('[MOCK] Personalization scoring – using mock results.')
        results = []
        for clause in clauses:
            # Placeholder formula
            r = round(clause.severity * 0.7, 4)
            if r >= 0.67:
                level = 'High'
            elif r >= 0.34:
                level = 'Medium'
            else:
                level = 'Low'

            results.append({
                'clause_id': clause.id,
                'relevance_score': r,
                'risk_level': level,
                'why_it_matters': (
                    f'[MOCK] This clause has a base severity of {clause.severity:.2f}. '
                    'Real scoring requires the personalization service.'
                ),
            })

        return {'user_id': user.id, 'results': results}


def get_personalization_client():
    if getattr(settings, 'USE_MOCK_PERSONALIZATION', True):
        return MockPersonalizationClient()
    return RealPersonalizationClient()
