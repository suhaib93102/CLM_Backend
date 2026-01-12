"""
URL configuration for clm_backend project.
"""
from django.contrib import admin
from django.urls import path, include
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rest_framework.routers import DefaultRouter
from health_views import HealthView, HealthDatabaseView, HealthCacheView, HealthMetricsView
from misc_views import AnalysisView, DocumentView, GenerationView
from admin_views import AdminViewSet, list_roles, list_permissions, list_users

router = DefaultRouter()
router.register(r'admin', AdminViewSet, basename='admin')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('contracts.urls')),
    path('api/', include('workflows.urls')),
    path('api/', include('notifications.urls')),
    path('api/', include('audit_logs.urls')),
    path('api/search/', include('search.urls')),
    path('api/', include('repository.urls')),
    path('api/', include('metadata.urls')),
    path('api/', include('ocr.urls')),
    path('api/', include('redaction.urls')),
    path('api/', include('ai.urls')),
    path('api/', include('rules.urls')),
    path('api/', include('approvals.urls')),
    path('api/', include('tenants.urls')),
    path('api/', include(router.urls)),
    path('api/roles/', list_roles, name='roles'),
    path('api/permissions/', list_permissions, name='permissions'),
    path('api/users/', list_users, name='users'),
    path('api/health/', HealthView.as_view(), name='health'),
    path('api/health/database/', HealthDatabaseView.as_view(), name='health-database'),
    path('api/health/cache/', HealthCacheView.as_view(), name='health-cache'),
    path('api/health/metrics/', HealthMetricsView.as_view(), name='health-metrics'),
    path('api/analysis/', AnalysisView.as_view(), name='analysis'),
    path('api/documents/', DocumentView.as_view(), name='documents'),
    path('api/generation/', GenerationView.as_view(), name='generation'),
]
