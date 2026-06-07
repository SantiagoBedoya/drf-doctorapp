from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    # Web GUI at root (dashboard, patients, doctors, appointments)
    path('', include('frontend.urls')),
    # API docs at api/schema/* (paths are absolute within docs.urls)
    path('', include('docs.urls')),
    # REST API at api/* (patients, doctors, bookings, prescriptions)
    path('', include('doctorapp.api_urls')),
]
