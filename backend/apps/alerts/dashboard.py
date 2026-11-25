"""
ClauseLens – Dashboard API.
Aggregates statistics from real database records.
"""
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.common.utils import success_response
from apps.documents.models import Document
from apps.analysis.models import Clause, AnalysisResult
from apps.monitoring.models import MonitoredPolicy, PolicyChange
from apps.alerts.models import Notification
from apps.alerts.serializers import NotificationSerializer
from apps.documents.serializers import DocumentSerializer
from apps.monitoring.serializers import PolicyChangeSerializer

logger = logging.getLogger('clauselens')


class DashboardView(APIView):
    """GET /api/dashboard/ – Return aggregated dashboard statistics."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Dashboard statistics',
        tags=['Dashboard'],
    )
    def get(self, request):
        user = request.user

        # Document stats
        docs = Document.objects.filter(user=user)
        documents_analyzed = docs.filter(status=Document.Status.COMPLETED).count()

        # Clause risk distribution (across all user's documents)
        user_clauses = Clause.objects.filter(document__user=user)
        high = user_clauses.filter(severity__gte=0.67).count()
        medium = user_clauses.filter(severity__gte=0.34, severity__lt=0.67).count()
        low = user_clauses.filter(severity__lt=0.34).count()
        high_risk_clauses = high

        # Monitoring
        policies_monitored = MonitoredPolicy.objects.filter(
            user=user, monitoring_status='active'
        ).count()

        # Changes detected
        changes_detected = PolicyChange.objects.filter(
            document__user=user,
        ).exclude(change_type='unchanged').count()

        # Recent data (last 5 of each)
        recent_docs = docs.order_by('-uploaded_at')[:5]
        recent_changes = PolicyChange.objects.filter(
            document__user=user,
        ).order_by('-detected_at')[:5]
        recent_notifications = Notification.objects.filter(
            user=user,
        ).order_by('-created_at')[:5]

        return success_response(
            data={
                'documents_analyzed': documents_analyzed,
                'high_risk_clauses': high_risk_clauses,
                'policies_monitored': policies_monitored,
                'changes_detected': changes_detected,
                'risk_distribution': {
                    'high': high,
                    'medium': medium,
                    'low': low,
                },
                'recent_documents': DocumentSerializer(
                    recent_docs, many=True, context={'request': request}
                ).data,
                'recent_changes': PolicyChangeSerializer(recent_changes, many=True).data,
                'recent_notifications': NotificationSerializer(recent_notifications, many=True).data,
            },
            message='Dashboard data retrieved.',
        )
