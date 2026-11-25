"""
ClauseLens – Analysis views.
"""
import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.common.utils import success_response, error_response
from apps.common.pagination import StandardResultsSetPagination
from apps.documents.models import Document
from .models import Clause, AnalysisResult
from .serializers import ClauseSerializer, AnalysisResultSerializer

logger = logging.getLogger('clauselens')


def _get_owned_document(pk, user):
    """Return (doc, None) or (None, error_response)."""
    try:
        doc = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return None, error_response('Document not found.', status_code=status.HTTP_404_NOT_FOUND)
    if doc.user != user:
        return None, error_response('Access denied.', status_code=status.HTTP_403_FORBIDDEN)
    return doc, None


class DocumentClausesView(APIView):
    """GET /api/analysis/documents/{id}/clauses/ – List all clauses for a document."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ClauseSerializer(many=True)},
        summary='List clauses for a document',
        tags=['Analysis'],
    )
    def get(self, request, pk):
        doc, err = _get_owned_document(pk, request.user)
        if err:
            return err
        clauses = Clause.objects.filter(document=doc).order_by('-severity')
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(clauses, request)
        serializer = ClauseSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        return success_response(data=response.data, message='Clauses retrieved.')


class DocumentAnalysisResultView(APIView):
    """GET /api/analysis/documents/{id}/result/ – Get analysis summary."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: AnalysisResultSerializer},
        summary='Get analysis result for a document',
        tags=['Analysis'],
    )
    def get(self, request, pk):
        doc, err = _get_owned_document(pk, request.user)
        if err:
            return err
        try:
            result = doc.analysis_result
        except AnalysisResult.DoesNotExist:
            return error_response(
                'Analysis result not available yet.',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return success_response(
            data=AnalysisResultSerializer(result).data,
            message='Analysis result retrieved.',
        )
