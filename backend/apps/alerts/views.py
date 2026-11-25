"""
ClauseLens – Notification / Alert views.
"""
import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.common.utils import success_response, error_response
from apps.common.pagination import StandardResultsSetPagination
from .models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger('clauselens')


class NotificationListView(APIView):
    """GET /api/notifications/ – List the user's notifications."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: NotificationSerializer(many=True)},
        summary='List notifications',
        tags=['Notifications'],
    )
    def get(self, request):
        qs = Notification.objects.filter(user=request.user)
        # Optional filter: ?unread=true
        if request.query_params.get('unread', '').lower() == 'true':
            qs = qs.filter(is_read=False)

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = NotificationSerializer(page, many=True)
        return success_response(
            data=paginator.get_paginated_response(serializer.data).data,
            message='Notifications retrieved.',
        )


class NotificationDetailView(APIView):
    """GET /api/notifications/{id}/ – Retrieve a single notification."""
    permission_classes = [IsAuthenticated]

    def _get(self, pk, user):
        try:
            return Notification.objects.get(pk=pk, user=user), None
        except Notification.DoesNotExist:
            return None, error_response('Notification not found.', status_code=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={200: NotificationSerializer},
        summary='Retrieve a notification',
        tags=['Notifications'],
    )
    def get(self, request, pk):
        n, err = self._get(pk, request.user)
        if err:
            return err
        return success_response(data=NotificationSerializer(n).data, message='Retrieved.')

    @extend_schema(summary='Delete a notification', tags=['Notifications'])
    def delete(self, request, pk):
        n, err = self._get(pk, request.user)
        if err:
            return err
        n.delete()
        return success_response(message='Notification deleted.')


class NotificationMarkReadView(APIView):
    """PATCH /api/notifications/{id}/read/ – Mark a notification as read."""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Mark notification as read', tags=['Notifications'])
    def patch(self, request, pk):
        try:
            n = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return error_response('Not found.', status_code=status.HTTP_404_NOT_FOUND)
        n.is_read = True
        n.save(update_fields=['is_read'])
        return success_response(message='Marked as read.')


class NotificationMarkAllReadView(APIView):
    """PATCH /api/notifications/read-all/ – Mark all notifications as read."""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Mark all notifications as read', tags=['Notifications'])
    def patch(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        return success_response(
            data={'marked_read': count},
            message=f'{count} notification(s) marked as read.',
        )
