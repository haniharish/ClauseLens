"""
ClauseLens – Account views (register, login, token, logout, me, change-password).
"""
import logging
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema

from apps.common.utils import success_response, error_response
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer

User = get_user_model()
logger = logging.getLogger('clauselens')


class RegisterView(APIView):
    """POST /api/auth/register/ – Create a new user account."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserSerializer},
        summary='Register a new user',
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message='Registration failed.',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.save()
        # Issue tokens immediately on registration
        refresh = RefreshToken.for_user(user)
        logger.info('New user registered: %s', user.email)
        return success_response(
            data={
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            message='Account created successfully.',
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/ – Obtain JWT access + refresh tokens.
    Wraps Simple JWT's TokenObtainPairView in the standard envelope.
    """
    @extend_schema(
        summary='Login and obtain JWT tokens',
        tags=['Authentication'],
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return success_response(
                data=response.data,
                message='Login successful.',
            )
        return error_response(
            message='Invalid credentials.',
            errors=response.data,
            status_code=response.status_code,
        )


class TokenRefreshWrappedView(TokenRefreshView):
    """POST /api/auth/token/refresh/ – Refresh access token."""
    @extend_schema(
        summary='Refresh access token',
        tags=['Authentication'],
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return success_response(data=response.data, message='Token refreshed.')
        return error_response(
            message='Token refresh failed.',
            errors=response.data,
            status_code=response.status_code,
        )


class LogoutView(APIView):
    """POST /api/auth/logout/ – Blacklist the refresh token."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Logout (blacklist refresh token)',
        tags=['Authentication'],
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return error_response(
                message='Refresh token is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as exc:
            return error_response(
                message='Invalid or expired token.',
                errors={'token': str(exc)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        logger.info('User logged out: %s', request.user.email)
        return success_response(message='Logged out successfully.')


class MeView(APIView):
    """GET /api/auth/me/ – Return the authenticated user's details."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserSerializer},
        summary='Get current user details',
        tags=['Authentication'],
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return success_response(data=serializer.data, message='User details retrieved.')


class ChangePasswordView(APIView):
    """POST /api/auth/change-password/ – Change the user's password."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        summary='Change password',
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return error_response(
                message='Password change failed.',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])
        logger.info('Password changed for user: %s', request.user.email)
        return success_response(message='Password changed successfully.')
