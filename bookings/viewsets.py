from rest_framework import viewsets

from bookings.filters import AppointmentFilter, AppointmentMedicalNoteFilter
from bookings.models import Appointment, MedicalNote
from bookings.serializers import AppointmentSerializer, MedicalNoteSerializer


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
