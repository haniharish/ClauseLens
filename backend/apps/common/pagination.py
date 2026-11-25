"""
ClauseLens – Standard pagination classes.
"""
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Default paginator: 20 items per page, max 100."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SmallResultsSetPagination(PageNumberPagination):
    """Small paginator for dashboard previews: 5 items per page."""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20
