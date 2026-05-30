import django_filters
from rest_framework import viewsets

from patients.serializers import (
    InsuranceSerializer,
    MedicalRecordSerializer,
    PatientSerializer,
)
from patients.models import Insurance, MedicalRecord, Patient


class PatientFilter(django_filters.FilterSet):
    class Meta:
        model = Patient
        fields = {
            'email': ['exact', 'icontains'],
            'contact_number': ['exact'],
        }


class InsuranceFilter(django_filters.FilterSet):
    class Meta:
        model = Insurance
        fields = {
            'patient_id': ['exact'],
            'provider': ['exact', 'icontains'],
            'expiration_date': ['exact', 'gte', 'lte'],
        }


class MedicalRecordFilter(django_filters.FilterSet):
    class Meta:
        model = MedicalRecord
        fields = {
            'patient_id': ['exact'],
            'date': ['exact', 'gte', 'lte'],
            'follow_up_date': ['exact', 'gte', 'lte'],
        }


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()
    filterset_class = PatientFilter
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['first_name', 'last_name', 'date_of_birth']
    ordering = ['first_name', 'last_name']


class InsuranceViewSet(viewsets.ModelViewSet):
    serializer_class = InsuranceSerializer
    queryset = Insurance.objects.all()
    filterset_class = InsuranceFilter
    search_fields = ['provider', 'policy_number']
    ordering_fields = ['provider', 'expiration_date']


class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    queryset = MedicalRecord.objects.all()
    filterset_class = MedicalRecordFilter
    ordering_fields = ['date', 'follow_up_date']
    ordering = ['-date']
