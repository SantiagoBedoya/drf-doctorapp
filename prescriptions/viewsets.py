from rest_framework import viewsets

from prescriptions.filters import MedicationFilter, PrescriptionFilter
from prescriptions.models import Medication, Prescription
from prescriptions.serializers import MedicationSerializer, PrescriptionSerializer


class MedicationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing the medication catalog."""

    serializer_class = MedicationSerializer
    queryset = Medication.objects.all()
    filterset_class = MedicationFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class PrescriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing prescriptions issued to patients."""

    serializer_class = PrescriptionSerializer
    queryset = Prescription.objects.all()
    filterset_class = PrescriptionFilter
    search_fields = [
        'dosage',
        'frequency',
        'duration',
        'notes',
        'patient__first_name',
        'patient__last_name',
        'doctor__first_name',
        'doctor__last_name',
        'medication__name',
    ]
    ordering_fields = ['start_date', 'end_date', 'prescribed_at', 'status']
    ordering = ['-prescribed_at']
