from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from datetime import date

from .models import AcademicYear, School, Course
from .serializers import (
    AcademicYearSerializer,
    SchoolSerializer,
    CourseListSerializer,
    CourseDetailSerializer,
    CourseCreateUpdateSerializer,
    PrerequisiteCourseSerializer
)


class AcademicYearViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing academic years.
    """
    queryset = AcademicYear.objects.all().order_by('-start_date')
    serializer_class = AcademicYearSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['name', 'start_date', 'end_date']
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Retrieve the current academic year.
        """
        try:
            current_year = AcademicYear.objects.get(is_active=True)
            serializer = self.get_serializer(current_year)
            return Response(serializer.data)
        except AcademicYear.DoesNotExist:
            return Response(
                {"detail": "No active academic year found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        """
        Retrieve all courses for a specific academic year.
        """
        academic_year = self.get_object()
        courses = academic_year.courses.all()
        
        # Apply filters if any
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            courses = courses.filter(is_active=is_active)
        
        # Apply credit hours filter if provided
        min_credits = request.query_params.get('min_credits')
        if min_credits is not None:
            courses = courses.filter(credit_hours__gte=int(min_credits))
        
        max_credits = request.query_params.get('max_credits')
        if max_credits is not None:
            courses = courses.filter(credit_hours__lte=int(max_credits))
        
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Set this academic year as the active one and deactivate others.
        """
        academic_year = self.get_object()
        
        # Deactivate all other academic years
        AcademicYear.objects.exclude(pk=academic_year.pk).update(is_active=False)
        
        # Activate this academic year
        academic_year.is_active = True
        academic_year.save()
        
        serializer = self.get_serializer(academic_year)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def for_date(self, request):
        """
        Find the academic year that includes a specific date.
        """
        target_date_str = request.query_params.get('date')
        if not target_date_str:
            return Response(
                {"detail": "Date parameter is required (YYYY-MM-DD)."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            target_date = date.fromisoformat(target_date_str)
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        matching_years = [
            year for year in AcademicYear.objects.all()
            if year.is_date_in_range(target_date)
        ]
        
        if not matching_years:
            return Response(
                {"detail": f"No academic year found for date {target_date_str}."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(matching_years, many=True)
        return Response(serializer.data)


class SchoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing schools.
    """
    queryset = School.objects.all().order_by('name')
    serializer_class = SchoolSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address', 'email_address']
    ordering_fields = ['name']


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing courses.
    """
    queryset = Course.objects.all().order_by('code')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['academic_year', 'is_active', 'credit_hours']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'credit_hours', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CourseCreateUpdateSerializer
        return CourseListSerializer
    
    @action(detail=True, methods=['get'])
    def prerequisites(self, request, pk=None):
        """
        Get all prerequisites for a specific course.
        """
        course = self.get_object()
        prerequisites = course.prerequisites.all()
        
        # Filter active prerequisites if requested
        active_only = request.query_params.get('active_only')
        if active_only and active_only.lower() == 'true':
            prerequisites = prerequisites.filter(is_active=True)
        
        serializer = PrerequisiteCourseSerializer(prerequisites, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def required_for(self, request, pk=None):
        """
        Get all courses that require this course as a prerequisite.
        """
        course = self.get_object()
        dependent_courses = course.required_for.all()
        
        # Filter active courses if requested
        active_only = request.query_params.get('active_only')
        if active_only and active_only.lower() == 'true':
            dependent_courses = dependent_courses.filter(is_active=True)
        
        serializer = PrerequisiteCourseSerializer(dependent_courses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def advanced(self, request):
        """
        Get all advanced courses (credit hours > 3).
        """
        advanced_courses = Course.objects.filter(credit_hours__gt=3)
        
        # Apply academic year filter if provided
        academic_year = request.query_params.get('academic_year')
        if academic_year:
            advanced_courses = advanced_courses.filter(academic_year=academic_year)
        
        # Apply active filter if provided
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            advanced_courses = advanced_courses.filter(is_active=is_active)
        
        serializer = self.get_serializer(advanced_courses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def without_prerequisites(self, request):
        """
        Get all courses that don't have prerequisites.
        """
        courses = Course.objects.annotate(
            prereq_count=Count('prerequisites')
        ).filter(prereq_count=0)
        
        # Apply academic year filter if provided
        academic_year = request.query_params.get('academic_year')
        if academic_year:
            courses = courses.filter(academic_year=academic_year)
        
        # Apply active filter if provided
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            courses = courses.filter(is_active=is_active)
        
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_prerequisite(self, request, pk=None):
        """
        Add a prerequisite to a course.
        """
        course = self.get_object()
        prerequisite_id = request.data.get('prerequisite_id')
        
        if not prerequisite_id:
            return Response(
                {"detail": "prerequisite_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            prerequisite = Course.objects.get(pk=prerequisite_id)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Prerequisite course not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check for circular reference
        if course.id == prerequisite.id:
            return Response(
                {"detail": "A course cannot be a prerequisite for itself"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if this would create a circular dependency chain
        if prerequisite.prerequisites.filter(pk=course.pk).exists():
            return Response(
                {"detail": "Adding this prerequisite would create a circular dependency"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add the prerequisite
        course.prerequisites.add(prerequisite)
        
        return Response(
            {"detail": f"Added {prerequisite.code} as a prerequisite for {course.code}"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def remove_prerequisite(self, request, pk=None):
        """
        Remove a prerequisite from a course.
        """
        course = self.get_object()
        prerequisite_id = request.data.get('prerequisite_id')
        
        if not prerequisite_id:
            return Response(
                {"detail": "prerequisite_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            prerequisite = Course.objects.get(pk=prerequisite_id)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Prerequisite course not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the course actually has this prerequisite
        if not course.prerequisites.filter(pk=prerequisite.pk).exists():
            return Response(
                {"detail": f"{prerequisite.code} is not a prerequisite for {course.code}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove the prerequisite
        course.prerequisites.remove(prerequisite)
        
        return Response(
            {"detail": f"Removed {prerequisite.code} as a prerequisite for {course.code}"},
            status=status.HTTP_200_OK
        )