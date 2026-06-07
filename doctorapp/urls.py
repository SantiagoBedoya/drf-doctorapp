"""
Root URL configuration for the doctor appointment management system.
Routes requests to the web GUI, REST API, admin interface, and API docs.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    # Web GUI at root (dashboard, patients, doctors, appointments)
    path('', include('frontend.urls')),
    # API docs at api/schema/* (docs.urls uses hardcoded absolute paths)
    path('', include('docs.urls')),
    # REST API at api/* (patients, doctors, bookings, prescriptions)
    path('', include('doctorapp.api_urls')),
]