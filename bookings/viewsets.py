import django_filters
from rest_framework import viewsets

from bookings.serializers import AppointmentSerializer, MedicalNoteSerializer
from bookings.models import Appointment, MedicalNote


class AppointmentFilter(django_filters.FilterSet):
    class Meta:
        model = Appointment
        fields = {
            'doctor_id': ['exact'],
            'patient_id': ['exact'],
            'status': ['exact'],
            'appointment_date': ['exact', 'gte', 'lte'],
            'appointment_time': ['exact', 'gte', 'lte'],
        }


class AppointmentMedicalNoteFilter(django_filters.FilterSet):
    class Meta:
        model = MedicalNote
        fields = {
            'appointment_id': ['exact'],
            'date': ['exact', 'gte', 'lte'],
        }


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()
    filterset_class = AppointmentFilter
    search_fields = ['notes', 'status']
    ordering_fields = ['appointment_date', 'appointment_time', 'status']
    ordering = ['-appointment_date', 'appointment_time']


class MedicalNoteViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalNoteSerializer
    queryset = MedicalNote.objects.all()
    filterset_class = AppointmentMedicalNoteFilter
    ordering_fields = ['date']
    ordering = ['-date']
