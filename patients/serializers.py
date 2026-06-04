from datetime import date
from rest_framework import serializers
from bookings.serializers import AppointmentSerializer
from patients.models import Insurance, MedicalRecord, Patient


class PatientSerializer(serializers.ModelSerializer):
    """Serializes patient data including nested appointments and computed age."""

    appointments = AppointmentSerializer(many=True, read_only=True, source='appointments')
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id',
            'first_name',
            'last_name',
            'age',
            'date_of_birth',
            'contact_number',
            'email',
            'address',
            'medical_history',
            'appointments',
        ]

    def get_age(self, obj):
        """Calculate the patient's age in years from their date of birth."""
        age_delta = date.today() - obj.date_of_birth
        return age_delta.days // 365


class InsuranceSerializer(serializers.ModelSerializer):
    """Serializes insurance policy data associated with a patient."""

    class Meta:
        model = Insurance
        fields = "__all__"


class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializes medical record data including diagnosis and treatment."""

    class Meta:
        model = MedicalRecord
        fields = "__all__"
