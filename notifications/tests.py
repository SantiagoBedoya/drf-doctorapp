from django.contrib.auth.models import User
from django.test import TestCase

from bookings.models import Appointment, AppointmentStatus
from doctors.models import Doctor
from notifications.models import Notification, NotificationType
from patients.models import Patient


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.doctor_user = User.objects.create_user(username="doctoruser", password="testpass")
        self.patient = Patient.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            email="john@example.com",
            contact_number="1234567890",
            address="123 Main St",
            medical_history="None",
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            first_name="Jane",
            last_name="Smith",
            qualification="MD",
            email="jane@example.com",
            contact_number="0987654321",
            address="456 Oak Ave",
            biography="Experienced doctor",
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date="2026-06-15",
            appointment_time="10:00",
            notes="Test appointment",
        )

    def test_create_notification(self):
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.APPOINTMENT_SCHEDULED,
            title="Test Notification",
            message="Test message",
            appointment=self.appointment,
        )
        self.assertEqual(str(notification), "[appointment_scheduled] Test Notification")
        self.assertFalse(notification.is_read)

    def test_notification_defaults(self):
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.APPOINTMENT_CONFIRMED,
            title="Confirmed",
            message="Your appointment is confirmed",
        )
        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.appointment)

    def test_notification_ordering(self):
        n1 = Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.APPOINTMENT_SCHEDULED,
            title="First",
            message="First notification",
        )
        n2 = Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.APPOINTMENT_SCHEDULED,
            title="Second",
            message="Second notification",
        )
        notifications = Notification.objects.all()
        self.assertEqual(notifications[0], n2)
        self.assertEqual(notifications[1], n1)

    def test_notification_str(self):
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.APPOINTMENT_CANCELLED,
            title="Cancelled",
            message="Appointment was cancelled",
        )
        expected = "[appointment_cancelled] Cancelled"
        self.assertEqual(str(notification), expected)

