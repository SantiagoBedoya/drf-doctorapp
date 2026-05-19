from rest_framework.routers import DefaultRouter
from bookings.viewsets import AppointmentViewSet, MedicalNoteViewSet


router = DefaultRouter()
router.register('appointments', AppointmentViewSet)
router.register('appointment-medical-notes', MedicalNoteViewSet)

urlpatterns = router.urls
