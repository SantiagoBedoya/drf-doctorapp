from django.contrib import admin

from bookings.models import Appointment, MedicalNote


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin configuration for managing appointments."""

    list_display = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date']
    search_fields = ['notes']


@admin.register(MedicalNote)
class MedicalNoteAdmin(admin.ModelAdmin):
    """Admin configuration for managing appointment medical notes."""

    list_display = ['appointment', 'date', 'note']
    list_filter = ['date']
