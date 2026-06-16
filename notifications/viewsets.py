from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for listing, creating, and managing notifications for the authenticated user."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.none()

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(recipient=self.request.user)

    def _check_notification_ownership(self, notification, request):
        """Verify the requesting user owns the notification, or deny permission."""
        if notification.recipient != request.user:
            self.permission_denied(request)

    @action(['POST'], detail=True, url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Mark a single notification as read after verifying ownership."""
        notification = self.get_object()
        self._check_notification_ownership(notification, request)
        notification.is_read = True
        notification.save()
        return Response({"status": "notification marked as read"})

    @action(['POST'], detail=False, url_path='mark-all-read')
    def mark_all_read(self, request):
        """Mark all unread notifications for the current user as read."""
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"status": "all notifications marked as read"})

    @action(['GET'], detail=False, url_path='unread-count')
    def unread_count(self, request):
        """Return the count of unread notifications for the current user."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread_count": count})
