"""
ClauseLens – Shared custom permissions.
"""
from rest_framework.permissions import BasePermission
from django.conf import settings


class IsOwner(BasePermission):
    """
    Object-level permission: only the owner of an object may access it.
    The object must have a `user` or `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, 'user', None) or getattr(obj, 'owner', None)
        return owner == request.user


class IsInternalService(BasePermission):
    """
    Allows access only to requests that carry the correct internal
    service token in the X-Internal-Token header.
    This is used to protect endpoints that only other microservices
    (NLP, version tracker, etc.) should call.
    """
    def has_permission(self, request, view):
        token = request.headers.get('X-Internal-Token', '')
        return bool(token and token == settings.INTERNAL_SERVICE_TOKEN)
