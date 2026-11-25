"""
ClauseLens – Shared response helpers and utilities.
"""
import logging
import hashlib
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('clauselens')


def success_response(data=None, message='Success', status_code=status.HTTP_200_OK):
    """Return a standardised successful API response."""
    payload = {
        'success': True,
        'message': message,
        'data': data or {},
    }
    return Response(payload, status=status_code)


def error_response(message='An error occurred', errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """Return a standardised error API response."""
    payload = {
        'success': False,
        'message': message,
        'errors': errors or {},
    }
    return Response(payload, status=status_code)


def hash_text(text: str) -> str:
    """Return SHA-256 hash of a string (used for version fingerprinting)."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def paginated_response(paginator, queryset, serializer_class, request, context=None):
    """Helper to paginate a queryset and return a standardised response."""
    page = paginator.paginate_queryset(queryset, request)
    ctx = {'request': request}
    if context:
        ctx.update(context)
    serializer = serializer_class(page, many=True, context=ctx)
    response = paginator.get_paginated_response(serializer.data)
    return Response({
        'success': True,
        'message': 'Data retrieved successfully',
        'data': response.data,
    })
