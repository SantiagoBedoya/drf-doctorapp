from django.db import models
from django.conf import settings
from bookings.models import Appointment


class NotificationType(models.TextChoices):
    APPOINTMENT_SCHEDULED = 'appointment_scheduled', 'Appointment Scheduled'
    APPOINTMENT_CONFIRMED = 'appointment_confirmed', 'Appointment Confirmed'
    APPOINTMENT_COMPLETED = 'appointment_completed', 'Appointment Completed'
    APPOINTMENT_CANCELLED = 'appointment_cancelled', 'Appointment Cancelled'
    APPOINTMENT_NO_SHOW = 'appointment_no_show', 'Appointment No Show'
    APPOINTMENT_REMINDER = 'appointment_reminder', 'Appointment Reminder'


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title}"
