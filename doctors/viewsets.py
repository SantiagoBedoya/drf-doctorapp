import django_filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from bookings.serializers import AppointmentSerializer
from doctors.permissions import IsDoctor
from doctors.serializers import (
    DepartmentSerializer,
    DoctorAvailabilitySerializer,
    DoctorReviewSerializer,
    DoctorSerializer,
    MedicalNoteSerializer,
)
from doctors.models import Department, Doctor, DoctorAvailability, DoctorReview, MedicalNote
from bookings.models import Appointment


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


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsDoctor]
    filterset_class = DoctorFilter
    search_fields = ['first_name', 'last_name', 'qualification', 'email', 'biography']
    ordering_fields = ['first_name', 'last_name', 'qualification', 'email']
    ordering = ['first_name', 'last_name']

    def _check_doctor_owner(self, request, doctor):
        """Verify the requesting user owns this doctor profile or is staff."""
        if not request.user.is_staff and (
            doctor.user is None or doctor.user != request.user
        ):
            self.permission_denied(
                request, message="You do not have permission to modify this doctor."
            )

    @action(['POST'], detail=True, url_path='set-on-vacation')
    def set_on_vacation(self, request, pk=None):
        """Mark a doctor as on vacation. Only the owner or staff can perform this."""
        doctor = self.get_object()
        self._check_doctor_owner(request, doctor)
        doctor.is_on_vacation = True
        doctor.save()
        return Response({"status": "The doctor is on vacation"})

    @action(['POST'], detail=True, url_path='set-off-vacation')
    def set_off_vacation(self, request, pk=None):
        """Mark a doctor as not on vacation. Only the owner or staff can perform this."""
        doctor = self.get_object()
        self._check_doctor_owner(request, doctor)
        doctor.is_on_vacation = False
        doctor.save()
        return Response({"status": "The doctor is not on vacation"})

    @action(['POST', 'GET'], detail=True, serializer_class=AppointmentSerializer)
    def appointments(self, request, pk=None):
        """List or create appointments for a specific doctor. POST requires owner/staff permissions."""
        doctor = self.get_object()
        data = request.data.copy()
        data['doctor'] = doctor.id

        if request.method == 'POST':
            if not request.user.is_staff and (
                doctor.user is None or doctor.user != request.user
            ):
                self.permission_denied(
                    request, message="You do not have permission to create appointments for this doctor."
                )
            serializer = AppointmentSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'GET':
            appointments = Appointment.objects.filter(doctor_id = pk)
            serializer = AppointmentSerializer(appointments, many=True)
            return Response(serializer.data)


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']


class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorAvailabilitySerializer
    queryset = DoctorAvailability.objects.all()
    filterset_class = DoctorAvailabilityFilter
    ordering_fields = ['start_date', 'end_date', 'start_time']


class MedicalNoteViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalNoteSerializer
    queryset = MedicalNote.objects.all()
    filterset_class = MedicalNoteFilter
    ordering_fields = ['date']
    ordering = ['-date']


class DoctorReviewViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorReviewSerializer
    queryset = DoctorReview.objects.all()
    filterset_class = DoctorReviewFilter
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
