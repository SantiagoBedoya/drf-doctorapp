"""
Frontend views for the doctor appointment management system.
Provides the dashboard, patient/doctor/appointment list and detail views.
"""

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import OperationalError
from django.views.generic import ListView, DetailView, TemplateView

from bookings.models import Appointment
from doctors.models import Doctor
from notifications.models import Notification
from patients.models import Patient

logger = logging.getLogger(__name__)


def _safe_count(model, label: str) -> int:
    """Return count of model objects, or 0 if the database is unavailable."""
    try:
        return model.objects.count()
    except OperationalError as e:
        logger.warning("Could not count %s: %s", label, e)
        return 0


class IndexView(LoginRequiredMixin, TemplateView):
    """Dashboard showing summary counts of patients, doctors, and appointments."""
    template_name = "frontend/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient_count"] = _safe_count(Patient, "patients")
        context["doctor_count"] = _safe_count(Doctor, "doctors")
        context["appointment_count"] = _safe_count(Appointment, "appointments")
        context["unread_notifications"] = self._get_unread_notification_count()
        return context

    def _get_unread_notification_count(self) -> int:
        """Return the count of unread notifications for the current user."""
        return Notification.objects.filter(
            recipient=self.request.user, is_read=False
        ).count()


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


class NotificationListView(LoginRequiredMixin, ListView):
    """Paginated list of notifications for the current user."""
    model = Notification
    template_name = "frontend/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
