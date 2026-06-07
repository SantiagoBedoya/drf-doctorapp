from django.views.generic import ListView, DetailView, TemplateView
from patients.models import Patient
from doctors.models import Doctor
from bookings.models import Appointment


class IndexView(TemplateView):
    template_name = "frontend/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient_count"] = Patient.objects.count()
        context["doctor_count"] = Doctor.objects.count()
        context["appointment_count"] = Appointment.objects.count()
        return context


class PatientListView(ListView):
    model = Patient
    template_name = "frontend/patient_list.html"
    context_object_name = "patients"
    paginate_by = 20


class PatientDetailView(DetailView):
    model = Patient
    template_name = "frontend/patient_detail.html"
    context_object_name = "patient"


class DoctorListView(ListView):
    model = Doctor
    template_name = "frontend/doctor_list.html"
    context_object_name = "doctors"
    paginate_by = 20


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = "frontend/doctor_detail.html"
    context_object_name = "doctor"


class AppointmentListView(ListView):
    model = Appointment
    template_name = "frontend/appointment_list.html"
    context_object_name = "appointments"
    paginate_by = 20
    ordering = ["-appointment_date", "-appointment_time"]


class AppointmentDetailView(DetailView):
    model = Appointment
    template_name = "frontend/appointment_detail.html"
    context_object_name = "appointment"
