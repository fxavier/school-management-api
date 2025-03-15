from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AcademicYearViewSet, SchoolViewSet, CourseViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'academic-years', AcademicYearViewSet)
router.register(r'schools', SchoolViewSet)
router.register(r'courses', CourseViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]