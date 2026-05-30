from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from bookings.models import Appointment
from bookings.serializers import AppointmentSerializer
from doctors.filters import (
    DoctorAvailabilityFilter,
    DoctorFilter,
    DoctorReviewFilter,
    MedicalNoteFilter,
)
from doctors.models import Department, Doctor, DoctorAvailability, DoctorReview, MedicalNote
from doctors.permissions import IsDoctor
from doctors.serializers import (
    DepartmentSerializer,
    DoctorAvailabilitySerializer,
    DoctorReviewSerializer,
    DoctorSerializer,
    MedicalNoteSerializer,
)


class DoctorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing doctor profiles. Requires authentication and doctor group membership."""

    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsDoctor]
    filterset_class = DoctorFilter
    search_fields = ['first_name', 'last_name', 'qualification', 'email', 'biography']
    ordering_fields = ['first_name', 'last_name', 'qualification', 'email']
    ordering = ['first_name', 'last_name']

    def _is_doctor_owner(self, request, doctor):
        """Check if the requesting user owns the doctor profile or is staff."""
        return request.user.is_staff or (
            doctor.user is not None and doctor.user == request.user
        )

    def _check_doctor_owner(self, request, doctor):
        if not self._is_doctor_owner(request, doctor):
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

    def _create_appointment(self, request, doctor):
        data = request.data.copy()
        data['doctor'] = doctor.id
        serializer = AppointmentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _list_appointments(self, pk):
        appointments = Appointment.objects.filter(doctor_id=pk)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    @action(['POST', 'GET'], detail=True, serializer_class=AppointmentSerializer)
    def appointments(self, request, pk=None):
        """List or create appointments for a specific doctor."""
        doctor = self.get_object()

        if request.method == 'POST':
            self._check_doctor_owner(request, doctor)
            return self._create_appointment(request, doctor)

        return self._list_appointments(pk)


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing medical departments. Publicly accessible."""

    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']


class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    """ViewSet for managing doctor availability schedules. Publicly accessible."""

    serializer_class = DoctorAvailabilitySerializer
    queryset = DoctorAvailability.objects.all()
    filterset_class = DoctorAvailabilityFilter
    ordering_fields = ['start_date', 'end_date', 'start_time']


class MedicalNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for managing medical notes linked to doctors."""

    serializer_class = MedicalNoteSerializer
    queryset = MedicalNote.objects.all()
    filterset_class = MedicalNoteFilter
    ordering_fields = ['date']
    ordering = ['-date']


class DoctorReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for managing patient reviews and ratings for doctors."""

    serializer_class = DoctorReviewSerializer
    queryset = DoctorReview.objects.all()
    filterset_class = DoctorReviewFilter
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
