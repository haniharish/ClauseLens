from django.urls import path
from .views import PersonalizedRiskListView

urlpatterns = [
    path('documents/<int:pk>/risks/', PersonalizedRiskListView.as_view(), name='personalized-risks'),
]
