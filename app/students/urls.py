from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentDocumentViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'documents', StudentDocumentViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]