"""
Consolidates all REST API URL routes into a single include.
Groups patient, doctor, booking, and prescription endpoints under /api/.
"""
from django.urls import path, include

urlpatterns = [
    path('api/', include('patients.urls')),
    path('api/', include('doctors.urls')),
    path('api/', include('bookings.urls')),
    path('api/', include('prescriptions.urls')),
    path('api/', include('notifications.urls')),
]
