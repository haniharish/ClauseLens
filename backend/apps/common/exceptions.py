"""
ClauseLens – Custom exception handler and DRF exception formatting.
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('clauselens')


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler that wraps all errors in the standard
    ClauseLens response envelope:
        { "success": false, "message": "...", "errors": {...} }
    """
    # Let DRF handle it first
    response = exception_handler(exc, context)

    if response is not None:
        message = _extract_message(response.data)
        errors = response.data if isinstance(response.data, dict) else {'detail': str(response.data)}

        response.data = {
            'success': False,
            'message': message,
            'errors': errors,
        }
    else:
        # Unhandled exception → 500
        logger.exception('Unhandled exception in view: %s', exc)
        response = Response(
            {
                'success': False,
                'message': 'An unexpected server error occurred.',
                'errors': {},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _extract_message(data) -> str:
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        # Return first error value
        for value in data.values():
            if isinstance(value, list) and value:
                return str(value[0])
            return str(value)
    if isinstance(data, list) and data:
        return str(data[0])
    return 'An error occurred.'
