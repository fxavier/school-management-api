import uuid
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import date
from core.utils import get_student_photo_path, get_student_document_path

class Gender(models.TextChoices):
    MALE = 'MALE', 'Masculino'
    FEMALE = 'FEMALE', 'Feminino'

    @classmethod
    def from_string(cls, value):
        if not value or not value.strip():
            return None
        return cls(value.upper())

class DocumentType(models.TextChoices):
    ID_CARD = 'ID_CARD', 'ID Card'
    BIRTH_CERTIFICATE = 'BIRTH_CERTIFICATE', 'Birth Certificate'
    PASSPORT = 'PASSPORT', 'Passport'
    
    @classmethod
    def from_string(cls, value):
        if not value or not value.strip():
            return None
        return cls(value.upper())


class GuardianRelationship(models.TextChoices):
    FATHER = 'FATHER', 'Pai'
    MOTHER = 'MOTHER', 'Mãe'
    GRANDPARENT = 'GRANDPARENT', 'Avô/Avó'
    BROTHER = 'BROTHER', 'Irmão'
    SISTER = 'SISTER', 'Irmã'
    UNCLE = 'UNCLE', 'Tio'
    AUNT = 'AUNT', 'Tia'
    COUSIN = 'COUSIN', 'Primo'
    OTHER = 'OTHER', 'Outro'

    @classmethod
    def from_string(cls, value):
        if not value or not value.strip():
            return None
        return cls(value.upper())


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)
    student_photo = models.ImageField(upload_to=get_student_photo_path, blank=True, null=True)
    student_address = models.TextField(blank=True, null=True)
    
    father_name = models.CharField(max_length=200, blank=True, null=True)
    father_phone_number = models.CharField(max_length=20, blank=True, null=True)
    father_email_address = models.EmailField(blank=True, null=True)
    
    mother_name = models.CharField(max_length=200, blank=True, null=True)
    mother_phone_number = models.CharField(max_length=20, blank=True, null=True)
    mother_email_address = models.EmailField(blank=True, null=True)
    
    guardian_name = models.CharField(max_length=200, blank=True, null=True)
    guardian_phone_number = models.CharField(max_length=20, blank=True, null=True)
    guardian_email_address = models.EmailField(blank=True, null=True)
    guardian_address = models.TextField(blank=True, null=True)
    guardian_relationship = models.CharField(
        max_length=20, 
        choices=GuardianRelationship.choices, 
        blank=True, 
        null=True
    )
    other_guardian_relationship = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_full_name(self):
        if self.middle_name and self.last_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        elif not self.middle_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.first_name
    
    def get_age(self):
        if not self.date_of_birth:
            return 0
        today = date.today()
        return relativedelta(today, self.date_of_birth).years
    
    def get_primary_contact_name(self):
        if self.guardian_relationship == GuardianRelationship.OTHER:
            return self.other_guardian_relationship
        return self.guardian_name
    
    def get_primary_contact_phone_number(self):
        if self.guardian_relationship == GuardianRelationship.FATHER:
            return self.father_phone_number
        elif self.guardian_relationship == GuardianRelationship.MOTHER:
            return self.mother_phone_number
        else:
            return self.guardian_phone_number
    
    def get_primary_contact_email_address(self):
        if self.guardian_relationship == GuardianRelationship.FATHER:
            return self.father_email_address
        elif self.guardian_relationship == GuardianRelationship.MOTHER:
            return self.mother_email_address
        else:
            return self.guardian_email_address
    
    def has_valid_identification(self):
        """Check if student has at least one valid identification document"""
        return self.documents.filter(
            is_verified=True
        ).exists()
    
    def get_primary_document(self):
        """Returns the primary identification document (prioritizing passport, then ID card, then birth certificate)"""
        # Try to get a passport first
        try:
            return self.documents.get(document_type=DocumentType.PASSPORT, is_verified=True)
        except StudentDocument.DoesNotExist:
            # Try to get an ID card
            try:
                return self.documents.get(document_type=DocumentType.ID_CARD, is_verified=True)
            except StudentDocument.DoesNotExist:
                # Try to get a birth certificate
                try:
                    return self.documents.get(document_type=DocumentType.BIRTH_CERTIFICATE, is_verified=True)
                except StudentDocument.DoesNotExist:
                    return None
    
    def get_document_numbers(self):
        """Returns a dictionary of document types and their numbers"""
        return {doc.get_document_type_display(): doc.document_number 
                for doc in self.documents.all()}
                
    def __str__(self):
        return self.get_full_name()


class StudentDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'Student',  # Using string reference to avoid circular import
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=20, 
        choices=DocumentType.choices
    )
    document_number = models.CharField(max_length=100)
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    issuing_authority = models.CharField(max_length=255, blank=True, null=True)
    document_file = models.FileField(
        upload_to=get_student_document_path, 
        blank=True, 
        null=True
    )
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateField(blank=True, null=True)
    verification_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'document_type']
        
    def __str__(self):
        return f"{self.get_document_type_display()} for {self.student.get_full_name()}"
    
    def is_expired(self):
        if not self.expiry_date:
            return False
        return date.today() > self.expiry_date
    
    def days_until_expiry(self):
        if not self.expiry_date:
            return None
        if self.is_expired():
            return 0
        return (self.expiry_date - date.today()).days