from datetime import date

from rest_framework import serializers
from bookings.models import Appointment, MedicalNote


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"

    def validate_appointment_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Cannot set an appointment in the past")
        return value

    def validate(self, attrs):
        if attrs.get("appointment_date") and attrs.get("appointment_time") and attrs.get("doctor"):
            conflicting = Appointment.objects.filter(
                doctor=attrs["doctor"],
                appointment_date=attrs["appointment_date"],
                appointment_time=attrs["appointment_time"],
                status__in=Appointment.CONFLICTING_STATUSES,
            )
            if self.instance:
                conflicting = conflicting.exclude(pk=self.instance.pk)
            if conflicting.exists():
                raise serializers.ValidationError(
                    f"The doctor already has an appointment on {attrs['appointment_date']} "
                    f"at {attrs['appointment_time']}"
                )
        return attrs


class MedicalNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalNote
        fields = "__all__"
