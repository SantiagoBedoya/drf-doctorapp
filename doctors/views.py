from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from doctors.serializers import DoctorSerializer, DepartmentSerializer, DoctorAvailabilitySerializer, MedicalNoteSerializer
from doctors.models import Doctor, Department, DoctorAvailability, MedicalNote


class ListDoctorsView(ListCreateAPIView):
    allowed_methods = ['GET', 'POST']
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all()


class DetailDoctorView(RetrieveUpdateDestroyAPIView):
    allowed_methods = ['GET', 'DELETE', 'PUT']
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all()


class ListDepartmentsView(ListCreateAPIView):
    allowed_methods = ['GET', 'POST']
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()


class DetailDepartmentView(RetrieveUpdateDestroyAPIView):
    allowed_methods = ['GET', 'DELETE', 'PUT']
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()


class ListDoctorAvailabilitiesView(ListCreateAPIView):
    serializer_class = DoctorAvailabilitySerializer

    def get_queryset(self):
        return DoctorAvailability.objects.filter(doctor_id = self.kwargs['pk'])


class DetailDoctorAvailabilityView(RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorAvailabilitySerializer
    lookup_url_kwarg = 'avail_pk'

    def get_queryset(self):
        return DoctorAvailability.objects.filter(doctor_id = self.kwargs['pk'])


class ListMedicalNotesView(ListCreateAPIView):
    serializer_class = MedicalNoteSerializer

    def get_queryset(self):
        return MedicalNote.objects.filter(doctor_id = self.kwargs['pk'])


class DetailMedicalNoteView(RetrieveUpdateDestroyAPIView):
    serializer_class = MedicalNoteSerializer
    lookup_url_kwarg = 'mn_pk'

    def get_queryset(self):
        return MedicalNote.objects.filter(doctor_id = self.kwargs['pk'])
