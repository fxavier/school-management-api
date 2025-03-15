from rest_framework import serializers
from .models import Student, StudentDocument, DocumentType, Gender, GuardianRelationship


class StudentPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['student_photo']
        
    def validate_student_photo(self, value):
        # Validate the file size (limit to 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image file too large ( > 5MB )")
        
        # Validate file type
        if not value.content_type.startswith('image'):
            raise serializers.ValidationError("File must be an image")
            
        return value

class StudentDocumentSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = StudentDocument
        fields = [
            'id', 'document_type', 'document_type_display', 'document_number',
            'issue_date', 'expiry_date', 'issuing_authority', 'document_file',
            'is_verified', 'verification_date', 'verification_notes',
            'days_until_expiry', 'is_expired', 'created_at', 'updated_at'
        ]


class StudentSerializer(serializers.ModelSerializer):
    documents = StudentDocumentSerializer(many=True, read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(source='get_age', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    guardian_relationship_display = serializers.CharField(source='get_guardian_relationship_display', read_only=True)
    primary_contact_name = serializers.CharField(source='get_primary_contact_name', read_only=True)
    primary_contact_phone = serializers.CharField(source='get_primary_contact_phone_number', read_only=True)
    primary_contact_email = serializers.EmailField(source='get_primary_contact_email_address', read_only=True)
    has_valid_identification = serializers.BooleanField(read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'student_number', 'first_name', 'middle_name', 'last_name', 
            'full_name', 'gender', 'gender_display', 'date_of_birth', 'age',
            'phone_number', 'email_address', 'student_photo', 'student_address',
            'father_name', 'father_phone_number', 'father_email_address',
            'mother_name', 'mother_phone_number', 'mother_email_address',
            'guardian_name', 'guardian_phone_number', 'guardian_email_address',
            'guardian_address', 'guardian_relationship', 'guardian_relationship_display',
            'other_guardian_relationship', 'primary_contact_name', 
            'primary_contact_phone', 'primary_contact_email',
            'has_valid_identification', 'documents', 'created_at', 'updated_at'
        ]


class StudentDocumentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = [
            'student', 'document_type', 'document_number', 'issue_date', 
            'expiry_date', 'issuing_authority', 'document_file', 
            'is_verified', 'verification_date', 'verification_notes'
        ]
        

class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'student_number', 'first_name', 'middle_name', 'last_name', 
            'gender', 'date_of_birth', 'phone_number', 'email_address', 
            'student_photo', 'student_address', 'father_name', 
            'father_phone_number', 'father_email_address', 'mother_name', 
            'mother_phone_number', 'mother_email_address', 'guardian_name', 
            'guardian_phone_number', 'guardian_email_address', 'guardian_address', 
            'guardian_relationship', 'other_guardian_relationship'
        ]
    
    def validate_gender(self, value):
        if value and value not in dict(Gender.choices).keys():
            raise serializers.ValidationError(f"Invalid gender. Choose from {dict(Gender.choices).keys()}")
        return value
    
    def validate_guardian_relationship(self, value):
        if value and value not in dict(GuardianRelationship.choices).keys():
            raise serializers.ValidationError(
                f"Invalid guardian relationship. Choose from {dict(GuardianRelationship.choices).keys()}"
            )
        return value
    
    def validate_student_photo(self, value):
        if value:
            # Validate the file size (limit to 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image file too large ( > 5MB )")
            
            # Validate file type
            if not value.content_type.startswith('image'):
                raise serializers.ValidationError("File must be an image")
               