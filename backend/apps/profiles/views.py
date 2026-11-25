"""
ClauseLens – Profile views.
"""
import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.common.utils import success_response, error_response
from .models import UserProfile
from .serializers import UserProfileSerializer

logger = logging.getLogger('clauselens')


class ProfileView(APIView):
    """
    GET  /api/profile/   – Retrieve current user's profile.
    POST /api/profile/   – Create profile (if none exists).
    PUT  /api/profile/   – Full update of profile.
    PATCH /api/profile/  – Partial update of profile.
    DELETE /api/profile/ – Delete profile.
    """
    permission_classes = [IsAuthenticated]

    def _get_profile(self, user):
        try:
            return UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return None

    @extend_schema(
        responses={200: UserProfileSerializer},
        summary='Get user profile',
        tags=['Profile'],
    )
    def get(self, request):
        profile = self._get_profile(request.user)
        if not profile:
            return error_response(
                message='Profile not found. Please create one.',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserProfileSerializer(profile)
        return success_response(data=serializer.data, message='Profile retrieved.')

    @extend_schema(
        request=UserProfileSerializer,
        responses={201: UserProfileSerializer},
        summary='Create user profile',
        tags=['Profile'],
    )
    def post(self, request):
        if self._get_profile(request.user):
            return error_response(
                message='Profile already exists. Use PUT or PATCH to update.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UserProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message='Profile creation failed.',
                errors=serializer.errors,
            )
        serializer.save(user=request.user)
        logger.info('Profile created for user: %s', request.user.email)
        return success_response(
            data=serializer.data,
            message='Profile created successfully.',
            status_code=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
        summary='Full update of user profile',
        tags=['Profile'],
    )
    def put(self, request):
        return self._update(request, partial=False)

    @extend_schema(
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
        summary='Partial update of user profile',
        tags=['Profile'],
    )
    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial):
        profile = self._get_profile(request.user)
        if not profile:
            return error_response(
                message='Profile not found. Please create one first.',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserProfileSerializer(profile, data=request.data, partial=partial)
        if not serializer.is_valid():
            return error_response(
                message='Profile update failed.',
                errors=serializer.errors,
            )
        serializer.save()
        logger.info('Profile updated for user: %s', request.user.email)
        return success_response(data=serializer.data, message='Profile updated.')

    @extend_schema(
        summary='Delete user profile',
        tags=['Profile'],
    )
    def delete(self, request):
        profile = self._get_profile(request.user)
        if not profile:
            return error_response(
                message='Profile not found.',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        profile.delete()
        logger.info('Profile deleted for user: %s', request.user.email)
        return success_response(message='Profile deleted successfully.')
