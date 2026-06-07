"""URL configuration for the prescriptions app, routing medication and prescription endpoints."""

from rest_framework.routers import DefaultRouter
from prescriptions.viewsets import MedicationViewSet, PrescriptionViewSet


router = DefaultRouter()
router.register('medications', MedicationViewSet)
router.register('prescriptions', PrescriptionViewSet)

urlpatterns = router.urls
