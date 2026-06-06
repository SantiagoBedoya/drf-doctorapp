from datetime import date, time, timedelta
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from doctors.models import Doctor
from patients.models import Patient
from bookings.models import Appointment, AppointmentStatus, MedicalNote
from bookings.serializers import AppointmentSerializer, MedicalNoteSerializer


class AppointmentModelTest(TestCase):
    """Tests for Appointment model creation and defaults."""

    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name="John",
            last_name="Doe",
            qualification="MD",
            contact_number="1234567890",
            email="john@example.com",
            address="123 Main St",
            biography="Cardiologist",
        )
        self.patient = Patient.objects.create(
            first_name="Jane",
            last_name="Patient",
            date_of_birth="1990-01-01",
            contact_number="0987654321",
            email="jane@example.com",
            address="456 Oak Ave",
            medical_history="None",
        )

    def test_appointment_creation(self):
        future_date = date.today() + timedelta(days=10)
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            appointment_time=time(10, 0),
            notes="Routine checkup",
            status=AppointmentStatus.SCHEDULED,
        )
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.appointment_date, future_date)
        self.assertEqual(appointment.appointment_time, time(10, 0))
        self.assertEqual(appointment.status, AppointmentStatus.SCHEDULED)

    def test_appointment_default_status(self):
        future_date = date.today() + timedelta(days=10)
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            notes="Default status",
        )
        self.assertEqual(appointment.status, AppointmentStatus.SCHEDULED)

    def test_appointment_patient_relation(self):
        future_date = date.today() + timedelta(days=10)
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            notes="Relation test",
        )
        self.assertIn(appointment, self.patient.appointments.all())

    def test_appointment_doctor_relation(self):
        future_date = date.today() + timedelta(days=10)
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            notes="Relation test",
        )
        self.assertIn(appointment, self.doctor.appointments.all())

    def test_doctor_cascade_delete(self):
        future_date = date.today() + timedelta(days=10)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            notes="Cascade test",
        )
        doctor_id = self.doctor.id
        self.doctor.delete()
        self.assertEqual(Appointment.objects.filter(doctor_id=doctor_id).count(), 0)

    def test_patient_cascade_delete(self):
        future_date = date.today() + timedelta(days=10)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            notes="Cascade test",
        )
        patient_id = self.patient.id
        self.patient.delete()
        self.assertEqual(Appointment.objects.filter(patient_id=patient_id).count(), 0)

    def test_conflicting_appointment_raises_error(self):
        future_date = date.today() + timedelta(days=10)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            appointment_time=time(10, 0),
            notes="First appointment",
            status=AppointmentStatus.SCHEDULED,
        )
        with self.assertRaises(Exception):
            Appointment.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                appointment_date=future_date,
                appointment_time=time(10, 0),
                notes="Conflicting appointment",
                status=AppointmentStatus.SCHEDULED,
            )

    def test_past_date_appointment_raises_error(self):
        past_date = date.today() - timedelta(days=10)
        with self.assertRaises(Exception):
            Appointment.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                appointment_date=past_date,
                notes="Past appointment",
            )

    def test_cancelled_appointment_does_not_conflict(self):
        future_date = date.today() + timedelta(days=10)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            appointment_time=time(10, 0),
            notes="Cancelled",
            status=AppointmentStatus.CANCELLED,
        )
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            appointment_time=time(10, 0),
            notes="New after cancelled",
            status=AppointmentStatus.SCHEDULED,
        )
        self.assertEqual(appointment.status, AppointmentStatus.SCHEDULED)

    def test_completed_appointment_does_not_conflict(self):
        future_date = date.today() + timedelta(days=10)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            appointment_time=time(10, 0),
            notes="Completed",
            status=AppointmentStatus.COMPLETED,
        )
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            appointment_time=time(10, 0),
            notes="New after completed",
            status=AppointmentStatus.SCHEDULED,
        )
        self.assertEqual(appointment.status, AppointmentStatus.SCHEDULED)

    def test_different_time_does_not_conflict(self):
        future_date = date.today() + timedelta(days=10)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            appointment_time=time(10, 0),
            notes="At 10:00",
            status=AppointmentStatus.SCHEDULED,
        )
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            appointment_time=time(11, 0),
            notes="At 11:00",
            status=AppointmentStatus.SCHEDULED,
        )
        self.assertEqual(appointment.appointment_time, time(11, 0))

    def test_different_date_does_not_conflict(self):
        future_date = date.today() + timedelta(days=10)
        next_day = future_date + timedelta(days=1)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            appointment_time=time(10, 0),
            notes="Day 1",
            status=AppointmentStatus.SCHEDULED,
        )
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=next_day,
            appointment_time=time(10, 0),
            notes="Day 2",
            status=AppointmentStatus.SCHEDULED,
        )
        self.assertEqual(appointment.appointment_date, next_day)

    def test_different_doctor_does_not_conflict(self):
        other_doctor = Doctor.objects.create(
            first_name="Sarah",
            last_name="Smith",
            qualification="PhD",
            contact_number="0987654321",
            email="sarah@example.com",
            address="789 Pine St",
            biography="Neurologist",
        )
        future_date = date.today() + timedelta(days=10)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            appointment_time=time(10, 0),
            notes="With Dr. Doe",
            status=AppointmentStatus.SCHEDULED,
        )
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=other_doctor,
            appointment_date=future_date,
            appointment_time=time(10, 0),
            notes="With Dr. Smith",
            status=AppointmentStatus.SCHEDULED,
        )
        self.assertEqual(appointment.doctor, other_doctor)

    def test_update_appointment_no_conflict_with_self(self):
        future_date = date.today() + timedelta(days=10)
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            appointment_time=time(10, 0),
            notes="Original",
            status=AppointmentStatus.SCHEDULED,
        )
        appointment.notes = "Updated notes"
        appointment.save()
        self.assertEqual(Appointment.objects.count(), 1)


class MedicalNoteModelTest(TestCase):
    """Tests for MedicalNote model creation, relations, and cascade delete."""

    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name="John",
            last_name="Doe",
            qualification="MD",
            contact_number="1234567890",
            email="john@example.com",
            address="123 Main St",
            biography="Cardiologist",
        )
        self.patient = Patient.objects.create(
            first_name="Jane",
            last_name="Patient",
            date_of_birth="1990-01-01",
            contact_number="0987654321",
            email="jane@example.com",
            address="456 Oak Ave",
            medical_history="None",
        )
        self.future_date = date.today() + timedelta(days=10)
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=self.future_date,
            notes="For medical note tests",
        )
        self.medical_note = MedicalNote.objects.create(
            appointment=self.appointment,
            note="Patient is responding well to treatment",
            date=self.future_date,
        )

    def test_medical_note_creation(self):
        note = MedicalNote.objects.get(id=self.medical_note.id)
        self.assertEqual(note.appointment, self.appointment)
        self.assertEqual(note.note, "Patient is responding well to treatment")
        self.assertEqual(note.date, self.future_date)

    def test_medical_note_appointment_relation(self):
        self.assertIn(self.medical_note, self.appointment.medical_notes.all())

    def test_appointment_cascade_delete(self):
        appointment_id = self.appointment.id
        self.appointment.delete()
        self.assertEqual(MedicalNote.objects.filter(appointment_id=appointment_id).count(), 0)

    def test_medical_note_empty_note_allowed(self):
        note = MedicalNote.objects.create(
            appointment=self.appointment,
            note="",
            date=date.today() + timedelta(days=15),
        )
        self.assertEqual(note.note, "")


class AppointmentSerializerTest(TestCase):
    """Tests for AppointmentSerializer validation."""

    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name="John",
            last_name="Doe",
            qualification="MD",
            contact_number="1234567890",
            email="john@example.com",
            address="123 Main St",
            biography="Cardiologist",
        )
        self.patient = Patient.objects.create(
            first_name="Jane",
            last_name="Patient",
            date_of_birth="1990-01-01",
            contact_number="0987654321",
            email="jane@example.com",
            address="456 Oak Ave",
            medical_history="None",
        )
        self.future_date = (date.today() + timedelta(days=10)).isoformat()
        self.valid_data = {
            "patient": self.patient.id,
            "doctor": self.doctor.id,
            "appointment_date": self.future_date,
            "appointment_time": "10:00:00",
            "notes": "Routine checkup",
            "status": "scheduled",
        }

    def test_valid_appointment_serializer(self):
        serializer = AppointmentSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_returns_correct_fields(self):
        serializer = AppointmentSerializer(data=self.valid_data)
        serializer.is_valid()
        self.assertEqual(
            serializer.validated_data["appointment_date"],
            date.fromisoformat(self.future_date),
        )

    def test_past_date_is_invalid(self):
        data = self.valid_data.copy()
        past_date = (date.today() - timedelta(days=10)).isoformat()
        data["appointment_date"] = past_date
        serializer = AppointmentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("appointment_date", serializer.errors)

    def test_past_date_error_message(self):
        data = self.valid_data.copy()
        past_date = (date.today() - timedelta(days=10)).isoformat()
        data["appointment_date"] = past_date
        serializer = AppointmentSerializer(data=data)
        serializer.is_valid()
        self.assertIn("past", str(serializer.errors["appointment_date"]).lower())

    def test_today_date_is_valid(self):
        data = self.valid_data.copy()
        data["appointment_date"] = date.today().isoformat()
        data["appointment_time"] = time(23, 59).isoformat()
        serializer = AppointmentSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_conflicting_appointment_is_invalid(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.fromisoformat(self.future_date),
            appointment_time=time(10, 0),
            notes="Existing",
            status=AppointmentStatus.SCHEDULED,
        )
        serializer = AppointmentSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())

    def test_conflicting_appointment_error_message(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.fromisoformat(self.future_date),
            appointment_time=time(10, 0),
            notes="Existing",
            status=AppointmentStatus.SCHEDULED,
        )
        serializer = AppointmentSerializer(data=self.valid_data)
        serializer.is_valid()
        errors = str(serializer.errors)
        self.assertIn("already has an appointment", errors.lower())

    def test_no_conflict_with_cancelled_appointment(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.fromisoformat(self.future_date),
            appointment_time=time(10, 0),
            notes="Cancelled existing",
            status=AppointmentStatus.CANCELLED,
        )
        serializer = AppointmentSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_no_conflict_with_no_show_appointment(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.fromisoformat(self.future_date),
            appointment_time=time(10, 0),
            notes="No show",
            status=AppointmentStatus.NO_SHOW,
        )
        serializer = AppointmentSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_no_conflict_different_time(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.fromisoformat(self.future_date),
            appointment_time=time(11, 0),
            notes="Different time",
            status=AppointmentStatus.SCHEDULED,
        )
        serializer = AppointmentSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_fields(self):
        serializer = AppointmentSerializer()
        expected_fields = {
            "id", "patient", "doctor", "appointment_date",
            "appointment_time", "notes", "status",
        }
        self.assertEqual(set(serializer.fields.keys()), expected_fields)


class MedicalNoteSerializerTest(TestCase):
    """Tests for MedicalNoteSerializer validation."""

    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name="John",
            last_name="Doe",
            qualification="MD",
            contact_number="1234567890",
            email="john@example.com",
            address="123 Main St",
            biography="Cardiologist",
        )
        self.patient = Patient.objects.create(
            first_name="Jane",
            last_name="Patient",
            date_of_birth="1990-01-01",
            contact_number="0987654321",
            email="jane@example.com",
            address="456 Oak Ave",
            medical_history="None",
        )
        future_date = date.today() + timedelta(days=10)
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            notes="For serializer tests",
        )

    def test_valid_medical_note_serializer(self):
        data = {
            "appointment": self.appointment.id,
            "note": "Patient is recovering",
            "date": (date.today() + timedelta(days=10)).isoformat(),
        }
        serializer = MedicalNoteSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_appointment_is_invalid(self):
        data = {
            "note": "Missing appointment",
            "date": (date.today() + timedelta(days=10)).isoformat(),
        }
        serializer = MedicalNoteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("appointment", serializer.errors)

    def test_missing_note_is_invalid(self):
        data = {
            "appointment": self.appointment.id,
            "date": (date.today() + timedelta(days=10)).isoformat(),
        }
        serializer = MedicalNoteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("note", serializer.errors)

    def test_serializer_fields(self):
        serializer = MedicalNoteSerializer()
        expected_fields = {"id", "appointment", "note", "date"}
        self.assertEqual(set(serializer.fields.keys()), expected_fields)


class AppointmentViewSetTest(APITestCase):
    """Tests CRUD operations for AppointmentViewSet endpoints."""

    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name="John",
            last_name="Doe",
            qualification="MD",
            contact_number="1234567890",
            email="john@example.com",
            address="123 Main St",
            biography="Cardiologist",
        )
        self.patient = Patient.objects.create(
            first_name="Jane",
            last_name="Patient",
            date_of_birth="1990-01-01",
            contact_number="0987654321",
            email="jane@example.com",
            address="456 Oak Ave",
            medical_history="None",
        )
        self.future_date = (date.today() + timedelta(days=10)).isoformat()
        self.valid_data = {
            "patient": self.patient.id,
            "doctor": self.doctor.id,
            "appointment_date": self.future_date,
            "appointment_time": "10:00:00",
            "notes": "Routine checkup",
            "status": "scheduled",
        }

    def test_list_appointments_empty(self):
        response = self.client.get("/api/appointments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_create_appointment(self):
        response = self.client.post("/api/appointments/", self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(response.data["notes"], "Routine checkup")
        self.assertEqual(response.data["status"], "scheduled")

    def test_list_appointments(self):
        self.client.post("/api/appointments/", self.valid_data, format="json")
        response = self.client.get("/api/appointments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_appointment(self):
        response = self.client.post("/api/appointments/", self.valid_data, format="json")
        appointment_id = response.data["id"]
        response = self.client.get(f"/api/appointments/{appointment_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["notes"], "Routine checkup")

    def test_retrieve_nonexistent_appointment_returns_404(self):
        response = self.client.get("/api/appointments/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_appointment(self):
        response = self.client.post("/api/appointments/", self.valid_data, format="json")
        appointment_id = response.data["id"]
        updated_data = self.valid_data.copy()
        updated_data["notes"] = "Updated checkup notes"
        response = self.client.put(
            f"/api/appointments/{appointment_id}/", updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["notes"], "Updated checkup notes")

    def test_partial_update_appointment(self):
        response = self.client.post("/api/appointments/", self.valid_data, format="json")
        appointment_id = response.data["id"]
        response = self.client.patch(
            f"/api/appointments/{appointment_id}/", {"notes": "Partial update"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["notes"], "Partial update")

    def test_delete_appointment(self):
        response = self.client.post("/api/appointments/", self.valid_data, format="json")
        appointment_id = response.data["id"]
        response = self.client.delete(f"/api/appointments/{appointment_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_delete_nonexistent_appointment_returns_404(self):
        response = self.client.delete("/api/appointments/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_appointment_past_date_returns_400(self):
        data = self.valid_data.copy()
        data["appointment_date"] = (date.today() - timedelta(days=10)).isoformat()
        response = self.client.post("/api/appointments/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_conflicting_appointment_returns_400(self):
        self.client.post("/api/appointments/", self.valid_data, format="json")
        response = self.client.post("/api/appointments/", self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_different_time_succeeds(self):
        self.client.post("/api/appointments/", self.valid_data, format="json")
        data = self.valid_data.copy()
        data["appointment_time"] = "11:00:00"
        response = self.client.post("/api/appointments/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_appointment_cancelled_does_not_conflict(self):
        response = self.client.post("/api/appointments/", self.valid_data, format="json")
        appointment_id = response.data["id"]
        self.client.patch(
            f"/api/appointments/{appointment_id}/",
            {"status": "cancelled"},
            format="json",
        )
        response = self.client.post("/api/appointments/", self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_filter_by_doctor(self):
        self.client.post("/api/appointments/", self.valid_data, format="json")
        response = self.client.get(f"/api/appointments/?doctor_id={self.doctor.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_by_patient(self):
        self.client.post("/api/appointments/", self.valid_data, format="json")
        response = self.client.get(f"/api/appointments/?patient_id={self.patient.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_by_status(self):
        self.client.post("/api/appointments/", self.valid_data, format="json")
        response = self.client.get("/api/appointments/?status=scheduled")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_by_status_no_match(self):
        self.client.post("/api/appointments/", self.valid_data, format="json")
        response = self.client.get("/api/appointments/?status=confirmed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_search_by_notes(self):
        self.client.post("/api/appointments/", self.valid_data, format="json")
        response = self.client.get("/api/appointments/?search=Routine")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_search_by_notes_no_match(self):
        self.client.post("/api/appointments/", self.valid_data, format="json")
        response = self.client.get("/api/appointments/?search=Emergency")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)


class AppointmentMedicalNoteViewSetTest(APITestCase):
    """Tests CRUD operations for MedicalNoteViewSet under bookings."""

    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name="John",
            last_name="Doe",
            qualification="MD",
            contact_number="1234567890",
            email="john@example.com",
            address="123 Main St",
            biography="Cardiologist",
        )
        self.patient = Patient.objects.create(
            first_name="Jane",
            last_name="Patient",
            date_of_birth="1990-01-01",
            contact_number="0987654321",
            email="jane@example.com",
            address="456 Oak Ave",
            medical_history="None",
        )
        future_date = date.today() + timedelta(days=10)
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=future_date,
            notes="For medical note tests",
        )

    def test_list_medical_notes_empty(self):
        response = self.client.get("/api/appointment-medical-notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_create_medical_note(self):
        data = {
            "appointment": self.appointment.id,
            "note": "Follow-up required",
            "date": (date.today() + timedelta(days=10)).isoformat(),
        }
        response = self.client.post("/api/appointment-medical-notes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicalNote.objects.count(), 1)

    def test_create_medical_note_without_appointment_returns_400(self):
        data = {
            "note": "No appointment",
            "date": (date.today() + timedelta(days=10)).isoformat(),
        }
        response = self.client.post("/api/appointment-medical-notes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_medical_note(self):
        note = MedicalNote.objects.create(
            appointment=self.appointment,
            note="Initial consultation",
            date=date.today() + timedelta(days=10),
        )
        response = self.client.get(f"/api/appointment-medical-notes/{note.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["note"], "Initial consultation")

    def test_retrieve_nonexistent_medical_note_returns_404(self):
        response = self.client.get("/api/appointment-medical-notes/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_medical_note(self):
        note = MedicalNote.objects.create(
            appointment=self.appointment,
            note="Initial consultation",
            date=date.today() + timedelta(days=10),
        )
        data = {"note": "Updated note"}
        response = self.client.patch(
            f"/api/appointment-medical-notes/{note.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertEqual(note.note, "Updated note")

    def test_delete_medical_note(self):
        note = MedicalNote.objects.create(
            appointment=self.appointment,
            note="Temporary note",
            date=date.today() + timedelta(days=10),
        )
        response = self.client.delete(f"/api/appointment-medical-notes/{note.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MedicalNote.objects.count(), 0)

    def test_filter_by_appointment(self):
        MedicalNote.objects.create(
            appointment=self.appointment,
            note="Note for appointment",
            date=date.today() + timedelta(days=10),
        )
        response = self.client.get(
            f"/api/appointment-medical-notes/?appointment_id={self.appointment.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
