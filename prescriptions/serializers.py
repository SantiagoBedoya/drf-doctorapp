from rest_framework import serializers

from prescriptions.models import Medication, Prescription


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = "__all__"


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = "__all__"
