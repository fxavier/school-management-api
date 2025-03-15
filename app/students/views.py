from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from .models import Student, StudentDocument, DocumentType
from .serializers import (
    StudentSerializer,
    StudentCreateUpdateSerializer,
    StudentDocumentSerializer,
    StudentDocumentCreateUpdateSerializer,
    StudentPhotoSerializer,
)


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing student information.
    
    list:
    Return a list of all students.
    
    create:
    Create a new student instance.
    
    retrieve:
    Return the given student.
    
    update:
    Update a student instance.
    
    partial_update:
    Update a student instance partially.
    
    destroy:
    Delete a student instance.
    """
    queryset = Student.objects.all().order_by('last_name', 'first_name')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'guardian_relationship']
    search_fields = ['first_name', 'last_name', 'student_number', 'email_address', 
                    'father_name', 'mother_name', 'guardian_name']
    ordering_fields = ['last_name', 'first_name', 'student_number', 'date_of_birth', 
                      'created_at', 'updated_at']
    parser_classes = [JSONParser, MultiPartParser, FormParser] 
                      
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StudentCreateUpdateSerializer
        elif self.action == 'upload_photo':
            return StudentPhotoSerializer
        return StudentSerializer

    def perform_create(self, serializer):
        # Handle the photo upload during creation
        photo = self.request.data.get('student_photo')
        if photo:
            serializer.save(student_photo=photo)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        # Handle the photo upload during update
        photo = self.request.data.get('student_photo')
        if photo:
            # If there's an existing photo, delete it first
            instance = self.get_object()
            if instance.student_photo:
                instance.student_photo.delete(save=False)
            serializer.save(student_photo=photo)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_photo(self, request, pk=None):
        """Upload a photo for the student"""
        student = self.get_object()
        
        if 'student_photo' not in request.data:
            return Response(
                {"error": "No photo provided. Use 'student_photo' field to upload an image."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        photo = request.data['student_photo']
        
        # Basic validation
        if not photo.content_type.startswith('image'):
            return Response(
                {"error": "Uploaded file is not an image"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete existing photo if present
        if student.student_photo:
            student.student_photo.delete(save=False)
        
        # Save the new photo
        student.student_photo = photo
        student.save()
        
        return Response(
            {"message": "Photo uploaded successfully", 
             "photo_url": student.student_photo.url if student.student_photo else None},
            status=status.HTTP_200_OK
        )
    
    
    @action(detail=True, methods=['delete'])
    def remove_photo(self, request, pk=None):
        """Remove the student's photo"""
        student = self.get_object()
        
        if student.student_photo:
            student.student_photo.delete()
            student.save()
            return Response({"message": "Photo removed successfully"}, status=status.HTTP_200_OK)
        
        return Response({"message": "No photo to remove"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get all documents for a specific student"""
        student = self.get_object()
        documents = student.documents.all()
        serializer = StudentDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search for students"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query parameter "q" is required'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        students = Student.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(student_number__icontains=query) |
            Q(email_address__icontains=query) |
            Q(father_name__icontains=query) |
            Q(mother_name__icontains=query) |
            Q(guardian_name__icontains=query)
        ).distinct()
        
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def missing_documents(self, request):
        """Get all students missing valid identification documents"""
        missing_docs = []
        students = Student.objects.all()
        
        for student in students:
            if not student.has_valid_identification():
                serializer = self.get_serializer(student)
                missing_docs.append(serializer.data)
        
        return Response(missing_docs)
    
    @action(detail=False, methods=['get'])
    def expiring_documents(self, request):
        """Get all students with documents expiring in the next 90 days"""
        days = int(request.query_params.get('days', 90))
        
        # Get students with documents expiring soon
        students_with_expiring_docs = Student.objects.filter(
            documents__is_expired=False,
            documents__expiry_date__isnull=False,
            documents__days_until_expiry__lte=days
        ).distinct()
        
        serializer = self.get_serializer(students_with_expiring_docs, many=True)
        return Response(serializer.data)


class StudentDocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing student documents.
    """
    queryset = StudentDocument.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document_type', 'is_verified']
    ordering_fields = ['issue_date', 'expiry_date', 'created_at', 'updated_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StudentDocumentCreateUpdateSerializer
        return StudentDocumentSerializer
    
    @action(detail=False, methods=['get'])
    def expiring(self, request):
        """Get documents expiring in the next X days (default 90 days)"""
        days = int(request.query_params.get('days', 90))
        
        # Filter documents expiring soon but not already expired
        expiring_docs = StudentDocument.objects.filter(
            is_expired=False,
            expiry_date__isnull=False,
            days_until_expiry__lte=days
        ).order_by('expiry_date')
        
        serializer = self.get_serializer(expiring_docs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get all expired documents"""
        expired_docs = StudentDocument.objects.filter(
            is_expired=True
        ).order_by('expiry_date')
        
        serializer = self.get_serializer(expired_docs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unverified(self, request):
        """Get all unverified documents"""
        unverified_docs = StudentDocument.objects.filter(
            is_verified=False
        ).order_by('-created_at')
        
        serializer = self.get_serializer(unverified_docs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Mark a document as verified"""
        document = self.get_object()
        notes = request.data.get('notes', '')
        
        document.is_verified = True
        document.verification_date = timezone.now().date()
        document.verification_notes = notes
        document.save()
        
        serializer = self.get_serializer(document)
        return Response(serializer.data)