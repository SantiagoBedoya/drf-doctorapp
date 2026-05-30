import django_filters

from doctors.models import Department, Doctor, DoctorAvailability, DoctorReview, MedicalNote


class DoctorFilter(django_filters.FilterSet):
    """Allows filtering doctors by vacation status, qualification, and email."""

    class Meta:
        model = Doctor
        fields = {
            'is_on_vacation': ['exact'],
            'qualification': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
        }


class DoctorAvailabilityFilter(django_filters.FilterSet):
    """Allows filtering availabilities by doctor and date range."""

    class Meta:
        model = DoctorAvailability
        fields = {
            'doctor_id': ['exact'],
            'start_date': ['exact', 'gte', 'lte'],
            'end_date': ['exact', 'gte', 'lte'],
        }


class MedicalNoteFilter(django_filters.FilterSet):
    """Allows filtering medical notes by doctor and date."""

    class Meta:
        model = MedicalNote
        fields = {
            'doctor_id': ['exact'],
            'date': ['exact', 'gte', 'lte'],
        }


class DoctorReviewFilter(django_filters.FilterSet):
    """Allows filtering reviews by doctor, patient, and rating."""

    class Meta:
        model = DoctorReview
        fields = {
            'doctor_id': ['exact'],
            'patient_id': ['exact'],
            'rating': ['exact', 'gte', 'lte'],
        }
