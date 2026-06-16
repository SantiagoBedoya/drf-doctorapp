from django.db.models.signals import post_save
from django.dispatch import receiver

from bookings.models import Appointment, AppointmentStatus
from notifications.models import Notification, NotificationType


def _create_notification(
    recipient,
    notification_type: str,
    title: str,
    message: str,
    appointment,
) -> None:
    """Create a notification for the given recipient with the provided details."""
    Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        appointment=appointment,
    )


@receiver(post_save, sender=Appointment)
def appointment_notification(sender, instance, created, **kwargs):
    """Send notifications to patient and doctor when an appointment is created or its status changes."""
    patient_user = instance.patient.user if hasattr(instance.patient, 'user') else None
    doctor_user = instance.doctor.user if instance.doctor.user else None

    if created:
        # New appointment: notify both parties that it has been scheduled
        if patient_user:
            _create_notification(
                recipient=patient_user,
                notification_type=NotificationType.APPOINTMENT_SCHEDULED,
                title="Appointment Scheduled",
                message=f"Your appointment with Dr. {instance.doctor} on {instance.appointment_date} has been scheduled.",
                appointment=instance,
            )
        if doctor_user:
            _create_notification(
                recipient=doctor_user,
                notification_type=NotificationType.APPOINTMENT_SCHEDULED,
                title="New Appointment Scheduled",
                message=f"New appointment with {instance.patient} on {instance.appointment_date}.",
                appointment=instance,
            )
    else:
        # Existing appointment updated: map status changes to notification types
        status_map = {
            AppointmentStatus.CONFIRMED: (
                NotificationType.APPOINTMENT_CONFIRMED,
                "Appointment Confirmed",
            ),
            AppointmentStatus.COMPLETED: (
                NotificationType.APPOINTMENT_COMPLETED,
                "Appointment Completed",
            ),
            AppointmentStatus.CANCELLED: (
                NotificationType.APPOINTMENT_CANCELLED,
                "Appointment Cancelled",
            ),
            AppointmentStatus.NO_SHOW: (
                NotificationType.APPOINTMENT_NO_SHOW,
                "Appointment No Show",
            ),
        }
        if instance.status in status_map:
            ntype, ntitle = status_map[instance.status]
            if patient_user:
                _create_notification(
                    recipient=patient_user,
                    notification_type=ntype,
                    title=ntitle,
                    message=f"Your appointment with Dr. {instance.doctor} on {instance.appointment_date} is now {instance.get_status_display()}.",
                    appointment=instance,
                )
            if doctor_user:
                _create_notification(
                    recipient=doctor_user,
                    notification_type=ntype,
                    title=ntitle,
                    message=f"Appointment with {instance.patient} on {instance.appointment_date} is now {instance.get_status_display()}.",
                    appointment=instance,
                )
