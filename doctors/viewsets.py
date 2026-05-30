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


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsDoctor]

    def _check_doctor_owner(self, request, doctor):
        if not request.user.is_staff and (
            doctor.user is None or doctor.user != request.user
        ):
            self.permission_denied(
                request, message="You do not have permission to modify this doctor."
            )

    @action(['POST'], detail=True, url_path='set-on-vacation')
    def set_on_vacation(self, request, pk):
        doctor = self.get_object()
        self._check_doctor_owner(request, doctor)
        doctor.is_on_vacation = True
        doctor.save()
        return Response({"status": "The doctor is on vacation"})

    @action(['POST'], detail=True, url_path='set-off-vacation')
    def set_off_vacation(self, request, pk):
        doctor = self.get_object()
        self._check_doctor_owner(request, doctor)
        doctor.is_on_vacation = False
        doctor.save()
        return Response({"status": "The doctor is not on vacation"})

    @action(['POST', 'GET'], detail=True, serializer_class=AppointmentSerializer)
    def appointments(self, request, pk):
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


class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorAvailabilitySerializer
    queryset = DoctorAvailability.objects.all()


class MedicalNoteViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalNoteSerializer
    queryset = MedicalNote.objects.all()


class DoctorReviewViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorReviewSerializer
    queryset = DoctorReview.objects.all()
