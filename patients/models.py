from django.db import models

class Patient(models.Model):
    """Represents a patient with personal details and medical history.

    Tracks demographic information and medical history for patient care.
    Related models: Insurance (insurances), MedicalRecord (medical_records).
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    medical_history = models.TextField()


class Insurance(models.Model):
    """Represents an insurance policy associated with a patient.

    Links a patient to their insurance provider and policy details.
    """

    patient = models.ForeignKey(Patient, related_name='insurances', on_delete=models.CASCADE)
    provider = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=100)
    expiration_date = models.DateField()


class MedicalRecord(models.Model):
    """Represents a medical record entry tracking diagnosis and treatment for a patient.

    Stores clinical data including diagnosis, treatment plan, and follow-up scheduling.
    """

    patient = models.ForeignKey(Patient, related_name='medical_records', on_delete=models.CASCADE)
    date = models.DateField()
    diagnosis = models.TextField()
    treatment = models.TextField()
    follow_up_date = models.DateField()
