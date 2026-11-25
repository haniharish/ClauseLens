"""
ClauseLens – Internal API endpoints called by other microservices.
Protected by X-Internal-Token header.
"""
from django.urls import path
from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.common.permissions import IsInternalService
from apps.common.utils import success_response, error_response
from .serializers import NLPResponseSerializer
from .services import AnalysisService


class NLPCallbackView(APIView):
    """
    POST /api/internal/nlp-callback/
    Called by the NLP module when analysis is complete.
    """
    permission_classes = [IsInternalService]
    authentication_classes = []  # No JWT required; uses internal token

    @extend_schema(
        request=NLPResponseSerializer,
        summary='[Internal] NLP module posts analysis results',
        tags=['Internal'],
    )
    def post(self, request):
        serializer = NLPResponseSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message='Invalid NLP response format.',
                errors=serializer.errors,
            )
        data = serializer.validated_data
        try:
            result = AnalysisService.store_nlp_results(
                document_id=data['document_id'],
                nlp_data=data,
            )
            return success_response(
                data={'analysis_id': result.id},
                message='Analysis results stored.',
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as exc:
            return error_response(
                message=f'Failed to store analysis: {exc}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VersionUpdateView(APIView):
    """
    POST /api/internal/version-update/
    Called by the Version Tracking module when new policy changes are detected.
    """
    permission_classes = [IsInternalService]
    authentication_classes = []

    @extend_schema(
        summary='[Internal] Version tracker posts policy changes',
        tags=['Internal'],
    )
    def post(self, request):
        from apps.monitoring.services import VersionUpdateService
        result = VersionUpdateService.handle_version_update(request.data)
        if result.get('error'):
            return error_response(
                message=result['error'],
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return success_response(
            data=result,
            message='Version update processed.',
            status_code=status.HTTP_201_CREATED,
        )


urlpatterns = [
    path('nlp-callback/', NLPCallbackView.as_view(), name='internal-nlp-callback'),
    path('version-update/', VersionUpdateView.as_view(), name='internal-version-update'),
]
