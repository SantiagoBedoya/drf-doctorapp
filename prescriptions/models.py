from django.db import models

from doctors.models import Doctor
from patients.models import Patient
from bookings.models import Appointment


class Medication(models.Model):
    """Represents a medication available in the system's catalog."""

    name = models.CharField(max_length=200)
    description = models.TextField()
    side_effects = models.TextField(blank=True, default='')
    contraindications = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PrescriptionStatus(models.TextChoices):
    """Defines the possible states of a prescription."""

    ACTIVE = 'active', 'Active'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class Prescription(models.Model):
    """Represents a medical prescription issued by a doctor for a patient."""

    patient = models.ForeignKey(
        Patient, related_name='prescriptions', on_delete=models.CASCADE
    )
    doctor = models.ForeignKey(
        Doctor, related_name='prescriptions', on_delete=models.CASCADE
    )
    appointment = models.ForeignKey(
        Appointment,
        related_name='prescriptions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    medication = models.ForeignKey(
        Medication, related_name='prescriptions', on_delete=models.CASCADE
    )
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=200)
    duration = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=PrescriptionStatus.choices,
        default=PrescriptionStatus.ACTIVE,
    )
    prescribed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-prescribed_at']
