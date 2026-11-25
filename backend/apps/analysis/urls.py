from django.urls import path
from .views import DocumentClausesView, DocumentAnalysisResultView

urlpatterns = [
    path('documents/<int:pk>/clauses/', DocumentClausesView.as_view(), name='document-clauses'),
    path('documents/<int:pk>/result/', DocumentAnalysisResultView.as_view(), name='document-analysis-result'),
]
