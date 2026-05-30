import django_filters

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
