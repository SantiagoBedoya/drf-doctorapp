from django.db import OperationalError
from django.views.generic import ListView, DetailView, TemplateView

from bookings.models import Appointment
from doctors.models import Doctor
from patients.models import Patient


def _get_dashboard_counts():
    try:
        return {
            "patient_count": Patient.objects.count(),
            "doctor_count": Doctor.objects.count(),
            "appointment_count": Appointment.objects.count(),
        }
    except OperationalError:
        return {
            "patient_count": 0,
            "doctor_count": 0,
            "appointment_count": 0,
        }


class IndexView(TemplateView):
    """Dashboard showing summary counts of patients, doctors, and appointments."""
    template_name = "frontend/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_get_dashboard_counts())
        return context


class PatientListView(ListView):
    """Paginated list of all patients."""
    model = Patient
    template_name = "frontend/patient_list.html"
    context_object_name = "patients"
    paginate_by = 20


class PatientDetailView(DetailView):
    """Detail view for a single patient, including insurance, records, and appointments."""
    model = Patient
    template_name = "frontend/patient_detail.html"
    context_object_name = "patient"


class DoctorListView(ListView):
    """Paginated list of all doctors."""
    model = Doctor
    template_name = "frontend/doctor_list.html"
    context_object_name = "doctors"
    paginate_by = 20


class DoctorDetailView(DetailView):
    """Detail view for a single doctor, including availability, reviews, and appointments."""
    model = Doctor
    template_name = "frontend/doctor_detail.html"
    context_object_name = "doctor"


class AppointmentListView(ListView):
    """Paginated list of all appointments, newest first."""
    model = Appointment
    template_name = "frontend/appointment_list.html"
    context_object_name = "appointments"
    paginate_by = 20
    ordering = ["-appointment_date", "-appointment_time"]


class AppointmentDetailView(DetailView):
    """Detail view for a single appointment, including medical notes."""
    model = Appointment
    template_name = "frontend/appointment_detail.html"
    context_object_name = "appointment"
