from rest_framework.routers import DefaultRouter
from notifications.viewsets import NotificationViewSet

router = DefaultRouter()
router.register('notifications', NotificationViewSet)

urlpatterns = router.urls
