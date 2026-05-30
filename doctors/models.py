from django.conf import settings
from django.db import models


class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        null=True,
        blank=True,
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    biography = models.TextField()
    is_on_vacation = models.BooleanField(default = False)


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()


class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='availabilities', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['start_date', 'start_time']

class MedicalNote(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='medical_notes', on_delete=models.CASCADE)
    note = models.TextField()
    date = models.DateField()


class DoctorReview(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='reviews', on_delete=models.CASCADE)
    patient = models.ForeignKey('patients.Patient', related_name='doctor_reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['doctor', 'patient']
