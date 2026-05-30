from rest_framework.routers import DefaultRouter
from doctors.viewsets import (
    DoctorAvailabilityViewSet,
    DoctorReviewViewSet,
    DoctorViewSet,
    DepartmentViewSet,
    MedicalNoteViewSet,
)


router = DefaultRouter()
router.register('doctors', DoctorViewSet)
router.register('departments', DepartmentViewSet)
router.register('availabilities', DoctorAvailabilityViewSet)
router.register('doctor-medical-notes', MedicalNoteViewSet)
router.register('doctor-reviews', DoctorReviewViewSet)

urlpatterns = router.urls
