from django.contrib import admin

from patients.models import Insurance, MedicalRecord, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'contact_number']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ['patient', 'provider', 'policy_number', 'expiration_date']
    list_filter = ['provider', 'expiration_date']


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date', 'diagnosis', 'follow_up_date']
    list_filter = ['date', 'follow_up_date']

    def diagnosis(self, obj):
        return obj.diagnosos[:50] + '...' if len(obj.diagnosos) > 50 else obj.diagnosos
    diagnosis.short_description = 'Diagnosis'
