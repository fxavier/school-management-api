from django.contrib import admin
from users.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from import_export.admin import ImportExportMixin
from .models import School, AcademicYear, Course
from students.models import Student, StudentDocument

class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )

class SchoolAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'email_address', 'website_url')
    search_fields = ('name', 'address', 'phone_number', 'email_address', 'website_url')
    list_filter = ('name', 'address', 'phone_number', 'email_address', 'website_url')

class AcademicYearAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    search_fields = ('name', 'start_date', 'end_date')
    list_filter = ('name', 'start_date', 'end_date', 'is_active')

class CourseAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('code', 'name', 'description', 'credit_hours', 'academic_year', 'is_active')
    search_fields = ('code', 'name', 'description')
    list_filter = ('code', 'name', 'description', 'credit_hours', 'academic_year', 'is_active')

class StudentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email_address', 'phone_number', 'date_of_birth', 'gender', 'student_address')
    search_fields = ('first_name', 'last_name', 'email_address', 'phone_number', 'date_of_birth', 'gender', 'student_address')
    list_filter = ('first_name', 'last_name', 'email_address', 'phone_number', 'date_of_birth', 'gender', 'student_address')

class StudentDocumentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('student', 'document_type', 'document_number', 'is_verified', 'verification_date')
    search_fields = ('student__first_name', 'student__last_name', 'document_type', 'document_number')
    list_filter = ('student__first_name', 'student__last_name', 'document_type', 'is_verified')

admin.site.register(User, UserAdmin)    
admin.site.register(School, SchoolAdmin)
admin.site.register(AcademicYear, AcademicYearAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentDocument, StudentDocumentAdmin)