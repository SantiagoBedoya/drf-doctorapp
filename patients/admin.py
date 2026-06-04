from django.contrib import admin

from patients.models import Insurance, MedicalRecord, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin configuration for managing patients."""

    list_display = ['first_name', 'last_name', 'email', 'contact_number']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    """Admin configuration for managing patient insurance policies."""

    list_display = ['patient', 'provider', 'policy_number', 'expiration_date']
    list_filter = ['provider', 'expiration_date']


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    """Admin configuration for managing patient medical records."""

    list_display = ['patient', 'date', 'get_diagnosis', 'follow_up_date']
    list_filter = ['date', 'follow_up_date']

    def get_diagnosis(self, obj):
        """Truncate and display the diagnosis text for the admin list view."""
        return obj.diagnosis[:50] + '...' if len(obj.diagnosis) > 50 else obj.diagnosis
    get_diagnosis.short_description = 'Diagnosis'
