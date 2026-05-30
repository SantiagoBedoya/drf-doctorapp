import re

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers
from doctors.models import Department, Doctor, DoctorAvailability, DoctorReview, MedicalNote

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = "__all__"

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format")
        return value

    def validate_contact_number(self, value):
        if not re.fullmatch(r'\d{7,15}', value):
            raise serializers.ValidationError(
                "Contact number must contain only digits (7-15 characters)"
            )
        return value

    def validate(self, attrs):
        if len(attrs['contact_number']) < 10 and attrs['is_on_vacation']:
            raise serializers.ValidationError("Set a contact number before go to your vacations")
        return super().validate(attrs)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAvailability
        fields = "__all__"


class MedicalNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalNote
        fields = "__all__"


class DoctorReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorReview
        fields = "__all__"

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
