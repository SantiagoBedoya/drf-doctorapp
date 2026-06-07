from django.contrib import admin

from prescriptions.models import Medication, Prescription


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    """Admin configuration for managing the medication catalog."""

    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    """Admin configuration for managing prescriptions."""

    list_display = [
        'patient',
        'doctor',
        'medication',
        'dosage',
        'frequency',
        'status',
        'prescribed_at',
    ]
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = [
        'patient__first_name',
        'patient__last_name',
        'doctor__first_name',
        'doctor__last_name',
        'medication__name',
        'dosage',
    ]
