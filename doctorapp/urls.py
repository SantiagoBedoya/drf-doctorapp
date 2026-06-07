from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('frontend.urls')),
    path('', include('docs.urls')),
    path('', include('doctorapp.api_urls')),
]
