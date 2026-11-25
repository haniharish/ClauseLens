from django.urls import path
from .views import (
    DocumentListView,
    DocumentUploadView,
    DocumentURLView,
    DocumentDetailView,
    DocumentStatusView,
)

urlpatterns = [
    path('', DocumentListView.as_view(), name='document-list'),
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('url/', DocumentURLView.as_view(), name='document-url'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('<int:pk>/status/', DocumentStatusView.as_view(), name='document-status'),
]
