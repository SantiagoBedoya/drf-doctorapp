from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from bookings.models import Appointment, MedicalNote
from bookings.serializers import AppointmentSerializer, MedicalNoteSerializer


class ListAppointmentsView(ListCreateAPIView):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()


class DetailAppointmentView(RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()


class ListMedicalNotesView(ListCreateAPIView):
    serializer_class = MedicalNoteSerializer

    def get_queryset(self):
        return MedicalNote.objects.filter(appointment_id = self.kwargs['pk'])


class DetailMedicalNoteView(RetrieveUpdateDestroyAPIView):
    serializer_class = MedicalNoteSerializer
    lookup_url_kwarg = 'mn_pk'

    def get_queryset(self):
        return MedicalNote.objects.filter(appointment_id = self.kwargs['pk'])
