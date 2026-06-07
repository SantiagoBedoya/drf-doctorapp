import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import OperationalError
from django.views.generic import ListView, DetailView, TemplateView

from bookings.models import Appointment
from doctors.models import Doctor
from patients.models import Patient

logger = logging.getLogger(__name__)


def get_patient_count():
    try:
        return Patient.objects.count()
    except OperationalError as e:
        logger.warning("Could not count patients: %s", e)
        return 0


def get_doctor_count():
    try:
        return Doctor.objects.count()
    except OperationalError as e:
        logger.warning("Could not count doctors: %s", e)
        return 0


def get_appointment_count():
    try:
        return Appointment.objects.count()
    except OperationalError as e:
        logger.warning("Could not count appointments: %s", e)
        return 0


class IndexView(LoginRequiredMixin, TemplateView):
    """Dashboard showing summary counts of patients, doctors, and appointments."""
    template_name = "frontend/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient_count"] = get_patient_count()
        context["doctor_count"] = get_doctor_count()
        context["appointment_count"] = get_appointment_count()
        return context


class PatientListView(LoginRequiredMixin, ListView):
    """Paginated list of all patients."""
    model = Patient
    template_name = "frontend/patient_list.html"
    context_object_name = "patients"
    paginate_by = 20


class PatientDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a single patient, including insurance, records, and appointments."""
    model = Patient
    template_name = "frontend/patient_detail.html"
    context_object_name = "patient"


class DoctorListView(LoginRequiredMixin, ListView):
    """Paginated list of all doctors."""
    model = Doctor
    template_name = "frontend/doctor_list.html"
    context_object_name = "doctors"
    paginate_by = 20


class DoctorDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a single doctor, including availability, reviews, and appointments."""
    model = Doctor
    template_name = "frontend/doctor_detail.html"
    context_object_name = "doctor"


class AppointmentListView(LoginRequiredMixin, ListView):
    """Paginated list of all appointments, newest first."""
    model = Appointment
    template_name = "frontend/appointment_list.html"
    context_object_name = "appointments"
    paginate_by = 20
    ordering = ["-appointment_date", "-appointment_time"]


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a single appointment, including medical notes."""
    model = Appointment
    template_name = "frontend/appointment_detail.html"
    context_object_name = "appointment"
