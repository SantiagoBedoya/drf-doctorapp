"""
URL configuration for the doctor appointment management system.
Routes the web GUI, API endpoints, admin interface, and API docs.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    # Root path: web GUI (dashboard, patient/doctor/appointment views)
    path('', include('frontend.urls')),
    # Root path: docs app uses absolute paths (api/schema/...)
    path('', include('docs.urls')),
    # API routes: grouped via doctorapp/api_urls.py
    path('', include('doctorapp.api_urls')),
]
