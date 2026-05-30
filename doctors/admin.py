from django.contrib import admin

from doctors.models import Department, Doctor, DoctorAvailability, DoctorReview, MedicalNote


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'qualification', 'email', 'is_on_vacation']
    list_filter = ['is_on_vacation', 'qualification']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'start_date', 'end_date', 'start_time', 'end_time']
    list_filter = ['start_date', 'end_date']


@admin.register(MedicalNote)
class MedicalNoteAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'note']
    list_filter = ['date']


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'patient', 'rating', 'created_at']
    list_filter = ['rating']
