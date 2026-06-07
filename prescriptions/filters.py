import django_filters

from prescriptions.models import Medication, Prescription


class MedicationFilter(django_filters.FilterSet):
    """Allows filtering medications by name."""

    class Meta:
        model = Medication
        fields = {
            'name': ['exact', 'icontains'],
        }


class PrescriptionFilter(django_filters.FilterSet):
    """Allows filtering prescriptions by patient, doctor, medication, and status."""

    class Meta:
        model = Prescription
        fields = {
            'patient_id': ['exact'],
            'doctor_id': ['exact'],
            'medication_id': ['exact'],
            'status': ['exact'],
            'start_date': ['exact', 'gte', 'lte'],
            'end_date': ['exact', 'gte', 'lte'],
        }
