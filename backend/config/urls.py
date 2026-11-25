"""
ClauseLens URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Schema & Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Auth
    path('api/auth/', include('apps.accounts.urls')),

    # Profile
    path('api/profile/', include('apps.profiles.urls')),

    # Documents
    path('api/documents/', include('apps.documents.urls')),

    # Analysis & Clauses
    path('api/analysis/', include('apps.analysis.urls')),

    # Personalization
    path('api/personalization/', include('apps.personalization.urls')),

    # Versions & Changes (from monitoring app)
    # Already included above via apps.monitoring.version_urls

    # Monitoring
    path('api/monitoring/', include('apps.monitoring.urls')),

    # Versions & Changes (from monitoring app)
    path('api/', include('apps.monitoring.version_urls')),

    # Alerts / Notifications
    path('api/notifications/', include('apps.alerts.urls')),

    # Dashboard (served from alerts app for aggregation)
    path('api/dashboard/', include('apps.alerts.dashboard_urls')),

    # Internal endpoints (for other microservices)
    path('api/internal/', include('apps.analysis.internal_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
