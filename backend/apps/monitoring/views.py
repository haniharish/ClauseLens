"""
ClauseLens – Monitoring views.
"""
import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.common.utils import success_response, error_response
from apps.common.pagination import StandardResultsSetPagination
from apps.documents.services import DocumentService
from .models import MonitoredPolicy, PolicyVersion, PolicyChange
from .serializers import (
    MonitoredPolicySerializer,
    PolicyVersionSerializer,
    PolicyChangeSerializer,
)

logger = logging.getLogger('clauselens')


class MonitoringListCreateView(APIView):
    """
    GET  /api/monitoring/ – List monitored policies.
    POST /api/monitoring/ – Add a new policy URL to monitor.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: MonitoredPolicySerializer(many=True)},
        summary='List monitored policies',
        tags=['Monitoring'],
    )
    def get(self, request):
        qs = MonitoredPolicy.objects.filter(user=request.user)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = MonitoredPolicySerializer(page, many=True)
        return success_response(
            data=paginator.get_paginated_response(serializer.data).data,
            message='Monitored policies retrieved.',
        )

    @extend_schema(
        request=MonitoredPolicySerializer,
        responses={201: MonitoredPolicySerializer},
        summary='Add a policy URL to monitor',
        tags=['Monitoring'],
    )
    def post(self, request):
        serializer = MonitoredPolicySerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('Validation failed.', errors=serializer.errors)

        # Also create a document record for this URL
        doc = DocumentService.create_from_url(
            user=request.user,
            url=serializer.validated_data['policy_url'],
            document_name=serializer.validated_data.get('policy_name', ''),
        )

        monitored = MonitoredPolicy.objects.create(
            user=request.user,
            document=doc,
            **serializer.validated_data,
        )
        return success_response(
            data=MonitoredPolicySerializer(monitored).data,
            message='Policy added to monitoring.',
            status_code=status.HTTP_201_CREATED,
        )


class MonitoringDetailView(APIView):
    """
    GET    /api/monitoring/{id}/ – Details.
    PATCH  /api/monitoring/{id}/ – Update settings (pause/resume/interval).
    DELETE /api/monitoring/{id}/ – Remove monitoring.
    """
    permission_classes = [IsAuthenticated]

    def _get(self, pk, user):
        try:
            m = MonitoredPolicy.objects.get(pk=pk, user=user)
            return m, None
        except MonitoredPolicy.DoesNotExist:
            return None, error_response('Not found.', status_code=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={200: MonitoredPolicySerializer},
        summary='Retrieve monitored policy details',
        tags=['Monitoring'],
    )
    def get(self, request, pk):
        m, err = self._get(pk, request.user)
        if err:
            return err
        return success_response(data=MonitoredPolicySerializer(m).data, message='Retrieved.')

    @extend_schema(
        request=MonitoredPolicySerializer,
        responses={200: MonitoredPolicySerializer},
        summary='Update monitoring settings (pause/resume/interval)',
        tags=['Monitoring'],
    )
    def patch(self, request, pk):
        m, err = self._get(pk, request.user)
        if err:
            return err
        serializer = MonitoredPolicySerializer(m, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response('Validation failed.', errors=serializer.errors)
        serializer.save()
        return success_response(data=serializer.data, message='Monitoring settings updated.')

    @extend_schema(summary='Remove monitoring for a policy', tags=['Monitoring'])
    def delete(self, request, pk):
        m, err = self._get(pk, request.user)
        if err:
            return err
        m.delete()
        return success_response(message='Policy removed from monitoring.')


class PolicyVersionListView(APIView):
    """GET /api/versions/ – List all versions across user's documents."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: PolicyVersionSerializer(many=True)},
        summary='List all policy versions',
        tags=['Versions'],
    )
    def get(self, request):
        qs = PolicyVersion.objects.filter(document__user=request.user)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = PolicyVersionSerializer(page, many=True)
        return success_response(
            data=paginator.get_paginated_response(serializer.data).data,
            message='Versions retrieved.',
        )


class DocumentVersionListView(APIView):
    """GET /api/versions/{document_id}/ – List versions for a specific document."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: PolicyVersionSerializer(many=True)},
        summary='List versions for a document',
        tags=['Versions'],
    )
    def get(self, request, document_id):
        qs = PolicyVersion.objects.filter(
            document_id=document_id,
            document__user=request.user,
        )
        serializer = PolicyVersionSerializer(qs, many=True)
        return success_response(data=serializer.data, message='Versions retrieved.')


class DocumentVersionCompareView(APIView):
    """GET /api/versions/{document_id}/compare/ – Compare last two versions."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Compare the last two versions of a document',
        tags=['Versions'],
    )
    def get(self, request, document_id):
        versions = PolicyVersion.objects.filter(
            document_id=document_id,
            document__user=request.user,
        ).order_by('-version_number')[:2]

        if versions.count() < 2:
            return error_response(
                'Not enough versions to compare.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        v_new, v_old = versions[0], versions[1]
        changes = PolicyChange.objects.filter(
            document_id=document_id,
        ).order_by('-detected_at')[:50]

        return success_response(
            data={
                'old_version': PolicyVersionSerializer(v_old).data,
                'new_version': PolicyVersionSerializer(v_new).data,
                'changes': PolicyChangeSerializer(changes, many=True).data,
            },
            message='Comparison retrieved.',
        )


class DocumentChangesView(APIView):
    """GET /api/changes/{document_id}/ – List all clause-level changes for a document."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: PolicyChangeSerializer(many=True)},
        summary='List policy changes for a document',
        tags=['Versions'],
    )
    def get(self, request, document_id):
        qs = PolicyChange.objects.filter(
            document_id=document_id,
            document__user=request.user,
        )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = PolicyChangeSerializer(page, many=True)
        return success_response(
            data=paginator.get_paginated_response(serializer.data).data,
            message='Changes retrieved.',
        )
