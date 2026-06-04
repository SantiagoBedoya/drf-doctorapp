from django.contrib import admin

from doctors.models import Department, Doctor, DoctorAvailability, DoctorReview, MedicalNote


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Admin configuration for managing doctors."""

    list_display = ['first_name', 'last_name', 'qualification', 'email', 'is_on_vacation']
    list_filter = ['is_on_vacation', 'qualification']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin configuration for managing medical departments."""

    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    """Admin configuration for managing doctor availability schedules."""

    list_display = ['doctor', 'start_date', 'end_date', 'start_time', 'end_time']
    list_filter = ['start_date', 'end_date']


@admin.register(MedicalNote)
class MedicalNoteAdmin(admin.ModelAdmin):
    """Admin configuration for managing doctor medical notes."""

    list_display = ['doctor', 'date', 'note']
    list_filter = ['date']


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    """Admin configuration for managing doctor reviews."""

    list_display = ['doctor', 'patient', 'rating', 'created_at']
    list_filter = ['rating']
