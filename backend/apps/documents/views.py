"""
ClauseLens – Document views.
"""
import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema

from apps.common.utils import success_response, error_response
from apps.common.permissions import IsOwner
from apps.common.pagination import StandardResultsSetPagination
from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer, DocumentURLSerializer
from .services import DocumentService

logger = logging.getLogger('clauselens')


class DocumentListView(APIView):
    """GET /api/documents/ – List all documents belonging to the authenticated user."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: DocumentSerializer(many=True)},
        summary='List user documents',
        tags=['Documents'],
    )
    def get(self, request):
        queryset = Document.objects.filter(user=request.user).order_by('-uploaded_at')
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = DocumentSerializer(page, many=True, context={'request': request})
        response = paginator.get_paginated_response(serializer.data)
        return success_response(data=response.data, message='Documents retrieved.')


class DocumentUploadView(APIView):
    """POST /api/documents/upload/ – Upload a PDF document."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=DocumentUploadSerializer,
        responses={201: DocumentSerializer},
        summary='Upload a PDF document',
        tags=['Documents'],
    )
    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message='File upload failed.',
                errors=serializer.errors,
            )
        doc = DocumentService.create_from_file(
            user=request.user,
            file=serializer.validated_data['file'],
            document_name=serializer.validated_data.get('document_name'),
        )
        return success_response(
            data=DocumentSerializer(doc, context={'request': request}).data,
            message='Document uploaded successfully. Processing has begun.',
            status_code=status.HTTP_201_CREATED,
        )


class DocumentURLView(APIView):
    """POST /api/documents/url/ – Submit a policy URL for analysis."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=DocumentURLSerializer,
        responses={201: DocumentSerializer},
        summary='Submit a policy URL',
        tags=['Documents'],
    )
    def post(self, request):
        serializer = DocumentURLSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message='URL submission failed.',
                errors=serializer.errors,
            )
        doc = DocumentService.create_from_url(
            user=request.user,
            url=serializer.validated_data['policy_url'],
            document_name=serializer.validated_data.get('document_name'),
        )
        return success_response(
            data=DocumentSerializer(doc, context={'request': request}).data,
            message='URL submitted successfully. Processing has begun.',
            status_code=status.HTTP_201_CREATED,
        )


class DocumentDetailView(APIView):
    """
    GET    /api/documents/{id}/ – Retrieve document detail.
    DELETE /api/documents/{id}/ – Delete a document.
    """
    permission_classes = [IsAuthenticated]

    def _get_document(self, pk, user):
        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return None, error_response(
                message='Document not found.',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if doc.user != user:
            return None, error_response(
                message='You do not have permission to access this document.',
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return doc, None

    @extend_schema(
        responses={200: DocumentSerializer},
        summary='Retrieve a document',
        tags=['Documents'],
    )
    def get(self, request, pk):
        doc, err = self._get_document(pk, request.user)
        if err:
            return err
        return success_response(
            data=DocumentSerializer(doc, context={'request': request}).data,
            message='Document retrieved.',
        )

    @extend_schema(
        summary='Delete a document',
        tags=['Documents'],
    )
    def delete(self, request, pk):
        doc, err = self._get_document(pk, request.user)
        if err:
            return err
        doc.delete()
        logger.info('Document %s deleted by user %s', pk, request.user.email)
        return success_response(message='Document deleted successfully.')


class DocumentStatusView(APIView):
    """GET /api/documents/{id}/status/ – Check document processing status."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Check document processing status',
        tags=['Documents'],
    )
    def get(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk, user=request.user)
        except Document.DoesNotExist:
            return error_response(
                message='Document not found.',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return success_response(
            data={'id': doc.id, 'status': doc.status, 'updated_at': doc.updated_at},
            message='Status retrieved.',
        )
