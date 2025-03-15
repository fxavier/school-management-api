import uuid
from django.db import models
from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator, MaxValueValidator


class AcademicYear(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    def is_date_in_range(self, date):
        return (date >= self.start_date) and (date <= self.end_date)
    
    def is_current_year(self):
        if not self.is_active:
            return False
        
        today = date.today()
        return today >= self.start_date and today <= self.end_date
    
    def get_duration_in_days(self):
        if not self.start_date or not self.end_date:
            return 0
        
        return (self.end_date - self.start_date).days + 1
    
    def __str__(self):
        return self.name

class School(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email_address = models.EmailField()
    website_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    credit_hours = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        default=3
    )
    academic_year = models.ForeignKey(
        AcademicYear, 
        on_delete=models.CASCADE, 
        related_name='courses'
    )
    is_active = models.BooleanField(default=True)
    prerequisites = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        blank=True,
        related_name='required_for'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['code', 'academic_year']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def has_prerequisites(self):
        return self.prerequisites.exists()
    
    def get_prerequisite_count(self):
        return self.prerequisites.count()
    
    def get_active_prerequisites(self):
        return self.prerequisites.filter(is_active=True)
    
    @property
    def is_advanced_course(self):
        return self.credit_hours > 3
