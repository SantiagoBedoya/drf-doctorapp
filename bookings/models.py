from datetime import date

from django.db import models
from django.core.exceptions import ValidationError

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

    CONFLICTING_STATUSES = {
        AppointmentStatus.SCHEDULED,
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.IN_PROGRESS,
    }

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

    def clean(self):
        if self.appointment_date and self.appointment_date < date.today():
            raise ValidationError("Cannot set an appointment in the past")

        if self.doctor_id and self.appointment_date and self.appointment_time and self.status in self.CONFLICTING_STATUSES:
            conflicting = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=self.appointment_date,
                appointment_time=self.appointment_time,
                status__in=self.CONFLICTING_STATUSES,
            )
            if self.pk:
                conflicting = conflicting.exclude(pk=self.pk)
            if conflicting.exists():
                raise ValidationError(
                    f"The doctor already has an appointment on {self.appointment_date} "
                    f"at {self.appointment_time}"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class MedicalNote(models.Model):
    """Represents a medical note associated with a specific appointment."""

    appointment = models.ForeignKey(Appointment, related_name='medical_notes', on_delete=models.CASCADE)
    note = models.TextField()
    date = models.DateField()
