from rest_framework import serializers
from .models import AcademicYear, School, Course

class AcademicYearSerializer(serializers.ModelSerializer):
    duration_in_days = serializers.IntegerField(source='get_duration_in_days', read_only=True)
    is_current = serializers.BooleanField(source='is_current_year', read_only=True)
    courses_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicYear
        fields = [
            'id', 'name', 'start_date', 'end_date', 'is_active', 
            'duration_in_days', 'is_current', 'courses_count'
        ]
    
    def get_courses_count(self, obj):
        return obj.courses.count()
    
    def validate(self, data):
        """
        Check that start_date is before end_date
        """
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("End date must be after start date")
        return data


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            'id', 'name', 'address', 'phone_number', 
            'email_address', 'website_url'
        ]


class CourseListSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    prerequisite_count = serializers.IntegerField(source='get_prerequisite_count', read_only=True)
    has_prerequisites = serializers.BooleanField(read_only=True)
    is_advanced_course = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name', 'credit_hours', 'academic_year', 
            'academic_year_name', 'is_active', 'prerequisite_count',
            'has_prerequisites', 'is_advanced_course', 'created_at'
        ]


class PrerequisiteCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'credit_hours', 'is_active']


class CourseDetailSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    prerequisites = PrerequisiteCourseSerializer(many=True, read_only=True)
    required_for = PrerequisiteCourseSerializer(many=True, read_only=True)
    has_prerequisites = serializers.BooleanField(read_only=True)
    prerequisite_count = serializers.IntegerField(source='get_prerequisite_count', read_only=True)
    is_advanced_course = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name', 'description', 'credit_hours',
            'academic_year', 'academic_year_name', 'is_active',
            'prerequisites', 'required_for', 'has_prerequisites',
            'prerequisite_count', 'is_advanced_course',
            'created_at', 'updated_at'
        ]


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'code', 'name', 'description', 'credit_hours',
            'academic_year', 'is_active', 'prerequisites'
        ]
    
    def validate_credit_hours(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError("Credit hours must be between 1 and 12")
        return value
    
    def validate(self, data):
        """
        Validate that prerequisites are not circular
        """
        if self.instance and 'prerequisites' in data:
            # Check for circular references when updating
            prerequisites = data.get('prerequisites', [])
            
            # Check if the course is trying to add itself as a prerequisite
            if self.instance in prerequisites:
                raise serializers.ValidationError(
                    "A course cannot be a prerequisite for itself"
                )
            
            # Check for circular reference chains
            for prereq in prerequisites:
                if self._check_circular_reference(self.instance, prereq):
                    raise serializers.ValidationError(
                        f"Circular reference detected with course {prereq.code}"
                    )
        
        return data
    
    def _check_circular_reference(self, course, prerequisite, visited=None):
        """
        Helper method to check for circular references in course prerequisites
        """
        if visited is None:
            visited = set()
        
        if course.id in visited:
            return False
        
        visited.add(course.id)
        
        # If the prerequisite has the original course as a prerequisite,
        # there's a circular reference
        if course in prerequisite.prerequisites.all():
            return True
        
        # Check each of the prerequisite's prerequisites
        for prereq_of_prereq in prerequisite.prerequisites.all():
            if self._check_circular_reference(course, prereq_of_prereq, visited):
                return True
        
        return False