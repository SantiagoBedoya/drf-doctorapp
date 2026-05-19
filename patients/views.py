from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from patients.serializers import PatientSerializer
from patients.models import Patient


class ListPatientsView(ListAPIView, CreateAPIView):
    allowed_methods = ['GET', 'POST']
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()


class DetailPatientView(RetrieveUpdateDestroyAPIView):
    allowed_methods = ['GET', 'DELETE', 'PUT']
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()
