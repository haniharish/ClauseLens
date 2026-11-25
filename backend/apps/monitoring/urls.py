from django.urls import path
from .views import (
    MonitoringListCreateView,
    MonitoringDetailView,
    PolicyVersionListView,
    DocumentVersionListView,
    DocumentVersionCompareView,
    DocumentChangesView,
)

# Monitoring endpoints
monitoring_urlpatterns = [
    path('', MonitoringListCreateView.as_view(), name='monitoring-list'),
    path('<int:pk>/', MonitoringDetailView.as_view(), name='monitoring-detail'),
]

# Version endpoints – mounted at /api/ in main urls.py via include
version_urlpatterns = [
    path('versions/', PolicyVersionListView.as_view(), name='version-list'),
    path('versions/<int:document_id>/', DocumentVersionListView.as_view(), name='version-document'),
    path('versions/<int:document_id>/compare/', DocumentVersionCompareView.as_view(), name='version-compare'),
    path('changes/<int:document_id>/', DocumentChangesView.as_view(), name='changes-document'),
]

urlpatterns = monitoring_urlpatterns
