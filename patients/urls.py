from rest_framework.routers import DefaultRouter
from patients.viewsets import (
    InsuranceViewSet,
    MedicalRecordViewSet,
    PatientViewSet,
)


router = DefaultRouter()
router.register('patients', PatientViewSet)
router.register('insurances', InsuranceViewSet)
router.register('medical-records', MedicalRecordViewSet)

urlpatterns = router.urls
