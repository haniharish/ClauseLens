"""
ClauseLens – Personalization views.
"""
import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.common.utils import success_response, error_response
from apps.common.pagination import StandardResultsSetPagination
from apps.documents.models import Document
from apps.analysis.models import Clause
from .models import PersonalizedRisk
from .serializers import PersonalizedRiskSerializer
from integrations.personalization_client import get_personalization_client

logger = logging.getLogger('clauselens')


class PersonalizedRiskListView(APIView):
    """
    GET /api/personalization/documents/{id}/risks/
    Return personalized risk scores for all clauses in a document.
    If not yet calculated, trigger the calculation.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: PersonalizedRiskSerializer(many=True)},
        summary='Get personalized risk scores for a document',
        tags=['Personalization'],
    )
    def get(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk, user=request.user)
        except Document.DoesNotExist:
            return error_response('Document not found.', status_code=status.HTTP_404_NOT_FOUND)

        clauses = Clause.objects.filter(document=doc)
        if not clauses.exists():
            return error_response(
                'No clauses found. Document may still be processing.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Try to get cached results first
        risks = PersonalizedRisk.objects.filter(user=request.user, clause__document=doc)

        if not risks.exists():
            # Trigger personalization service
            risks = _request_personalization(request.user, clauses)
            if risks is None:
                return error_response(
                    'Personalization service is unavailable. Please try again later.',
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(risks, request)
        serializer = PersonalizedRiskSerializer(page, many=True)
        return success_response(
            data=paginator.get_paginated_response(serializer.data).data,
            message='Personalized risks retrieved.',
        )


def _request_personalization(user, clauses):
    """
    Call the personalization service and store results.
    Returns queryset of PersonalizedRisk or None on failure.
    """
    try:
        profile = user.profile
    except Exception:
        profile = None

    try:
        client = get_personalization_client()
        response = client.score_clauses(user=user, profile=profile, clauses=clauses)
    except Exception as exc:
        logger.error('Personalization service error: %s', exc)
        return None

    results = response.get('results', [])
    risk_objects = []
    for item in results:
        try:
            clause = Clause.objects.get(pk=item['clause_id'])
            risk_objects.append(PersonalizedRisk(
                user=user,
                clause=clause,
                relevance_score=item['relevance_score'],
                risk_level=item['risk_level'],
                why_it_matters=item['why_it_matters'],
            ))
        except (Clause.DoesNotExist, KeyError) as exc:
            logger.warning('Skipping personalization result: %s', exc)

    if risk_objects:
        PersonalizedRisk.objects.bulk_create(risk_objects, ignore_conflicts=True)

    return PersonalizedRisk.objects.filter(user=user, clause__in=clauses)
