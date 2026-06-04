from rest_framework import serializers
from bookings.models import Appointment, MedicalNote


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializes appointment data. Status validation is handled by model choices."""

    class Meta:
        model = Appointment
        fields = "__all__"


class MedicalNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalNote
        fields = "__all__"
