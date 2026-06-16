"""
URL configuration for the frontend web GUI.
Provides browseable pages for patients, doctors, and appointments.
"""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("patients/", views.PatientListView.as_view(), name="patient_list"),
    path("patients/<int:pk>/", views.PatientDetailView.as_view(), name="patient_detail"),
    path("doctors/", views.DoctorListView.as_view(), name="doctor_list"),
    path("doctors/<int:pk>/", views.DoctorDetailView.as_view(), name="doctor_detail"),
    path("appointments/", views.AppointmentListView.as_view(), name="appointment_list"),
    path("appointments/<int:pk>/", views.AppointmentDetailView.as_view(), name="appointment_detail"),
    path("notifications/", views.NotificationListView.as_view(), name="notification_list"),
]
