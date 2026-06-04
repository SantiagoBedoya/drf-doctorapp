import django_filters
from rest_framework import viewsets

from patients.serializers import (
    InsuranceSerializer,
    MedicalRecordSerializer,
    PatientSerializer,
)
from patients.models import Insurance, MedicalRecord, Patient


class PatientFilter(django_filters.FilterSet):
    """Allows filtering patients by email and contact number."""

    class Meta:
        model = Patient
        fields = {
            'email': ['exact', 'icontains'],
            'contact_number': ['exact'],
        }


class InsuranceFilter(django_filters.FilterSet):
    """Allows filtering insurance records by patient, provider, and expiration date."""

    class Meta:
        model = Insurance
        fields = {
            'patient_id': ['exact'],
            'provider': ['exact', 'icontains'],
            'expiration_date': ['exact', 'gte', 'lte'],
        }


class MedicalRecordFilter(django_filters.FilterSet):
    """Allows filtering medical records by patient, date, and follow-up date."""

    class Meta:
        model = MedicalRecord
        fields = {
            'patient_id': ['exact'],
            'date': ['exact', 'gte', 'lte'],
            'follow_up_date': ['exact', 'gte', 'lte'],
        }


class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet for listing, creating, updating, and deleting patients."""

    serializer_class = PatientSerializer
    queryset = Patient.objects.all()
    filterset_class = PatientFilter
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['first_name', 'last_name', 'date_of_birth']
    ordering = ['first_name', 'last_name']


class InsuranceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing insurance policies associated with patients."""

    serializer_class = InsuranceSerializer
    queryset = Insurance.objects.all()
    filterset_class = InsuranceFilter
    search_fields = ['provider', 'policy_number']
    ordering_fields = ['provider', 'expiration_date']


class MedicalRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for managing medical records and their diagnosis/treatment data."""

    serializer_class = MedicalRecordSerializer
    queryset = MedicalRecord.objects.all()
    filterset_class = MedicalRecordFilter
    ordering_fields = ['date', 'follow_up_date']
    ordering = ['-date']
