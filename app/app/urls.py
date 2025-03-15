"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from students.views import (
    # Student-related viewsets
    StudentViewSet, 
    StudentDocumentViewSet,
)

from core.views import (
    AcademicYearViewSet, 
    SchoolViewSet, 
    CourseViewSet
)

schema_view = get_schema_view(
    openapi.Info(
        title="School Management API",
        default_version='v1',
        description="API for managing students, courses, and academic records",
        terms_of_service="https://www.yourschool.com/terms/",
        contact=openapi.Contact(email="contact@yourschool.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = DefaultRouter()

# Student management endpoints
router.register(r'students', StudentViewSet)
router.register(r'documents', StudentDocumentViewSet)

# Academic system endpoints
router.register(r'academic-years', AcademicYearViewSet)
router.register(r'schools', SchoolViewSet)
router.register(r'courses', CourseViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('students.urls')),
    path('api/v1/', include('core.urls')),

    # Swagger UI endpoints
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
