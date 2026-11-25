from django.urls import path
from .views import (
    PolicyVersionListView,
    DocumentVersionListView,
    DocumentVersionCompareView,
    DocumentChangesView,
)

urlpatterns = [
    path('versions/', PolicyVersionListView.as_view(), name='version-list'),
    path('versions/<int:document_id>/', DocumentVersionListView.as_view(), name='version-document'),
    path('versions/<int:document_id>/compare/', DocumentVersionCompareView.as_view(), name='version-compare'),
    path('changes/<int:document_id>/', DocumentChangesView.as_view(), name='changes-document'),
]
