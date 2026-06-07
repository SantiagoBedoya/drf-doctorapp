from rest_framework import serializers

from prescriptions.models import Medication, Prescription


class MedicationSerializer(serializers.ModelSerializer):
    """Serializes medication catalog data including name, description, and side effects."""

    class Meta:
        model = Medication
        fields = "__all__"


class PrescriptionSerializer(serializers.ModelSerializer):
    """Serializes prescription data linking patients, doctors, and medications."""

    class Meta:
        model = Prescription
        fields = "__all__"
