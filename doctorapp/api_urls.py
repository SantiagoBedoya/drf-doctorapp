from django.urls import path, include

urlpatterns = [
    path('api/', include('patients.urls')),
    path('api/', include('doctors.urls')),
    path('api/', include('bookings.urls')),
    path('api/', include('prescriptions.urls')),
]
