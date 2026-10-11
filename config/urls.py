"""
URL configuration for CareBridge Healthcare API project.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Admin Interface
    path("admin/", admin.site.urls),

    # Root redirect to Swagger Documentation
    path("", RedirectView.as_view(url="/api/docs/", permanent=False), name="index"),

    # Authentication Endpoints
    path("api/auth/", include("healthcare.auth_urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Healthcare Core Endpoints (Patients, Doctors, Mappings)
    path("api/", include("healthcare.urls")),

    # API Documentation (OpenAPI Schema, Swagger UI, ReDoc)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
