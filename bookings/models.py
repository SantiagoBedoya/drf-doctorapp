from django.db import models

from doctors.models import Doctor
from patients.models import Patient


class AppointmentStatus(models.TextChoices):
    """Defines the possible states of a medical appointment."""

    SCHEDULED = 'scheduled', 'Scheduled'
    CONFIRMED = 'confirmed', 'Confirmed'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    NO_SHOW = 'no_show', 'No Show'


class Appointment(models.Model):
    """Represents a scheduled appointment between a patient and a doctor."""

    patient = models.ForeignKey(Patient, related_name='appointments', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='appointments', on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField(null=True, blank=True)
    notes = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.SCHEDULED,
    )


class MedicalNote(models.Model):
    """Represents a medical note associated with a specific appointment."""

    appointment = models.ForeignKey(Appointment, related_name='medical_notes', on_delete=models.CASCADE)
    note = models.TextField()
    date = models.DateField()
