from datetime import date, time
from django.contrib.auth.models import User, Group
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from doctors.models import Doctor, Department, DoctorAvailability, MedicalNote
from doctors.serializers import DepartmentSerializer, DoctorAvailabilitySerializer, DoctorSerializer, MedicalNoteSerializer
from patients.models import Patient


class DoctorModelTest(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name="John",
            last_name="Doe",
            qualification="MD",
            contact_number="1234567890",
            email="john@example.com",
            address="123 Main St",
            biography="Experienced cardiologist",
            is_on_vacation=False,
        )

    def test_doctor_creation(self):
        doctor = Doctor.objects.get(id=self.doctor.id)
        self.assertEqual(doctor.first_name, "John")
        self.assertEqual(doctor.last_name, "Doe")
        self.assertEqual(doctor.qualification, "MD")
        self.assertEqual(doctor.contact_number, "1234567890")
        self.assertEqual(doctor.email, "john@example.com")
        self.assertEqual(doctor.address, "123 Main St")
        self.assertEqual(doctor.biography, "Experienced cardiologist")
        self.assertFalse(doctor.is_on_vacation)

    def test_doctor_default_vacation_false(self):
        doctor = Doctor.objects.create(
            first_name="Jane",
            last_name="Smith",
            qualification="PhD",
            contact_number="0987654321",
            email="jane@example.com",
            address="456 Oak Ave",
            biography="Neurologist",
        )
        self.assertFalse(doctor.is_on_vacation)

    def test_doctor_on_vacation_true(self):
        self.doctor.is_on_vacation = True
        self.doctor.save()
        doctor = Doctor.objects.get(id=self.doctor.id)
        self.assertTrue(doctor.is_on_vacation)


class DepartmentModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(
            name="Cardiology",
            description="Heart and cardiovascular system",
        )

    def test_department_creation(self):
        department = Department.objects.get(id=self.department.id)
        self.assertEqual(department.name, "Cardiology")
        self.assertEqual(department.description, "Heart and cardiovascular system")


class DoctorAvailabilityModelTest(TestCase):
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
        self.availability = DoctorAvailability.objects.create(
            doctor=self.doctor,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def test_availability_creation(self):
        availability = DoctorAvailability.objects.get(id=self.availability.id)
        self.assertEqual(availability.doctor, self.doctor)
        self.assertEqual(availability.start_date, date(2025, 1, 1))
        self.assertEqual(availability.end_date, date(2025, 12, 31))
        self.assertEqual(availability.start_time, time(9, 0))
        self.assertEqual(availability.end_time, time(17, 0))

    def test_availability_doctor_relation(self):
        self.assertIn(self.availability, self.doctor.availabilities.all())

    def test_doctor_cascade_delete(self):
        doctor_id = self.doctor.id
        self.doctor.delete()
        self.assertEqual(DoctorAvailability.objects.filter(doctor_id=doctor_id).count(), 0)


class MedicalNoteModelTest(TestCase):
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
        self.note = MedicalNote.objects.create(
            doctor=self.doctor,
            note="Patient is recovering well",
            date=date(2025, 6, 15),
        )

    def test_note_creation(self):
        note = MedicalNote.objects.get(id=self.note.id)
        self.assertEqual(note.doctor, self.doctor)
        self.assertEqual(note.note, "Patient is recovering well")
        self.assertEqual(note.date, date(2025, 6, 15))

    def test_note_doctor_relation(self):
        self.assertIn(self.note, self.doctor.medical_notes.all())

    def test_doctor_cascade_delete(self):
        doctor_id = self.doctor.id
        self.doctor.delete()
        self.assertEqual(MedicalNote.objects.filter(doctor_id=doctor_id).count(), 0)


class DoctorSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "qualification": "MD",
            "contact_number": "1234567890",
            "email": "john@example.com",
            "address": "123 Main St",
            "biography": "Cardiologist",
            "is_on_vacation": False,
        }

    def test_valid_doctor_serializer(self):
        serializer = DoctorSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_returns_correct_fields(self):
        serializer = DoctorSerializer(data=self.valid_data)
        serializer.is_valid()
        self.assertEqual(serializer.validated_data["first_name"], "John")
        self.assertEqual(serializer.validated_data["last_name"], "Doe")

    def test_email_validation_requires_example_com(self):
        data = self.valid_data.copy()
        data["email"] = "john@gmail.com"
        serializer = DoctorSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_email_validation_error_message(self):
        data = self.valid_data.copy()
        data["email"] = "john@gmail.com"
        serializer = DoctorSerializer(data=data)
        serializer.is_valid()
        self.assertIn("example.com", str(serializer.errors["email"]))

    def test_email_validation_passes_with_example_com(self):
        data = self.valid_data.copy()
        data["email"] = "test@example.com"
        serializer = DoctorSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_raises_error_when_short_contact_and_on_vacation(self):
        data = self.valid_data.copy()
        data["contact_number"] = "123456789"
        data["is_on_vacation"] = True
        serializer = DoctorSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_validate_passes_when_short_contact_not_on_vacation(self):
        data = self.valid_data.copy()
        data["contact_number"] = "123456789"
        serializer = DoctorSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_passes_when_long_contact_on_vacation(self):
        data = self.valid_data.copy()
        data["is_on_vacation"] = True
        serializer = DoctorSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_uses_all_fields(self):
        serializer = DoctorSerializer()
        expected_fields = {
            "id", "first_name", "last_name", "qualification",
            "contact_number", "email", "address", "biography", "is_on_vacation",
        }
        self.assertEqual(set(serializer.fields.keys()), expected_fields)


class DepartmentSerializerTest(TestCase):
    def test_valid_department_serializer(self):
        data = {"name": "Cardiology", "description": "Heart care"}
        serializer = DepartmentSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_department_missing_name_is_invalid(self):
        data = {"description": "Heart care"}
        serializer = DepartmentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_department_serializer_fields(self):
        serializer = DepartmentSerializer()
        self.assertEqual(set(serializer.fields.keys()), {"id", "name", "description"})


class DoctorAvailabilitySerializerTest(TestCase):
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

    def test_valid_availability_serializer(self):
        data = {
            "doctor": self.doctor.id,
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "start_time": "09:00:00",
            "end_time": "17:00:00",
        }
        serializer = DoctorAvailabilitySerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_availability_missing_doctor_is_invalid(self):
        data = {
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "start_time": "09:00:00",
            "end_time": "17:00:00",
        }
        serializer = DoctorAvailabilitySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("doctor", serializer.errors)


class MedicalNoteSerializerTest(TestCase):
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

    def test_valid_note_serializer(self):
        data = {
            "doctor": self.doctor.id,
            "note": "Patient is recovering",
            "date": "2025-06-15",
        }
        serializer = MedicalNoteSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_note_missing_note_field_is_invalid(self):
        data = {
            "doctor": self.doctor.id,
            "date": "2025-06-15",
        }
        serializer = MedicalNoteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("note", serializer.errors)

    def test_note_missing_doctor_is_invalid(self):
        data = {
            "note": "Patient is recovering",
            "date": "2025-06-15",
        }
        serializer = MedicalNoteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("doctor", serializer.errors)


class BaseAuthTestCase(APITestCase):
    def setUp(self):
        self.doctor_user = User.objects.create_user(
            username="doctor1", password="testpass123"
        )
        self.doctors_group, _ = Group.objects.get_or_create(name="doctors")
        self.doctor_user.groups.add(self.doctors_group)

        self.regular_user = User.objects.create_user(
            username="regular", password="testpass123"
        )

        self.doctor = Doctor.objects.create(
            first_name="John",
            last_name="Doe",
            qualification="MD",
            contact_number="1234567890",
            email="john@example.com",
            address="123 Main St",
            biography="Cardiologist",
            is_on_vacation=False,
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


class DoctorViewSetPermissionsTest(BaseAuthTestCase):
    def test_list_requires_doctor_group(self):
        response = self.client.get("/api/doctors/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_authenticated_but_not_doctor_group_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/doctors/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_authenticated_doctor_returns_200(self):
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get("/api/doctors/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_unauthenticated_returns_403(self):
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "qualification": "PhD",
            "contact_number": "0987654321",
            "email": "jane@example.com",
            "address": "456 Oak Ave",
            "biography": "Neurologist",
            "is_on_vacation": False,
        }
        response = self.client.post("/api/doctors/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_unauthenticated_returns_403(self):
        response = self.client.delete(f"/api/doctors/{self.doctor.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DoctorViewSetCRUDTest(BaseAuthTestCase):
    def test_list_doctors(self):
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get("/api/doctors/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["first_name"], "John")

    def test_retrieve_doctor(self):
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get(f"/api/doctors/{self.doctor.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "John")
        self.assertEqual(response.data["email"], "john@example.com")

    def test_retrieve_nonexistent_doctor_returns_404(self):
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get("/api/doctors/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_doctor(self):
        self.client.force_authenticate(user=self.doctor_user)
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "qualification": "PhD",
            "contact_number": "0987654321",
            "email": "jane@example.com",
            "address": "456 Oak Ave",
            "biography": "Neurologist",
            "is_on_vacation": False,
        }
        response = self.client.post("/api/doctors/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Doctor.objects.count(), 2)
        self.assertEqual(response.data["first_name"], "Jane")

    def test_create_doctor_with_invalid_email_returns_400(self):
        self.client.force_authenticate(user=self.doctor_user)
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "qualification": "PhD",
            "contact_number": "0987654321",
            "email": "jane@gmail.com",
            "address": "456 Oak Ave",
            "biography": "Neurologist",
            "is_on_vacation": False,
        }
        response = self.client.post("/api/doctors/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_full_update_doctor(self):
        self.client.force_authenticate(user=self.doctor_user)
        data = {
            "first_name": "Johnny",
            "last_name": "Doe",
            "qualification": "MD",
            "contact_number": "1234567890",
            "email": "johnny@example.com",
            "address": "456 New St",
            "biography": "Updated biography",
            "is_on_vacation": True,
        }
        response = self.client.put(
            f"/api/doctors/{self.doctor.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.first_name, "Johnny")
        self.assertEqual(self.doctor.biography, "Updated biography")
        self.assertTrue(self.doctor.is_on_vacation)

    def test_partial_update_doctor(self):
        self.client.force_authenticate(user=self.doctor_user)
        data = {
            "biography": "Partially updated biography",
            "contact_number": self.doctor.contact_number,
            "is_on_vacation": self.doctor.is_on_vacation,
        }
        response = self.client.patch(
            f"/api/doctors/{self.doctor.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.biography, "Partially updated biography")

    def test_delete_doctor(self):
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.delete(f"/api/doctors/{self.doctor.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Doctor.objects.count(), 0)

    def test_delete_nonexistent_doctor_returns_404(self):
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.delete("/api/doctors/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DoctorViewSetCustomActionsTest(BaseAuthTestCase):
    def test_set_on_vacation(self):
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.post(
            f"/api/doctors/{self.doctor.id}/set-on-vacation/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "The doctor is on vacation")
        self.doctor.refresh_from_db()
        self.assertTrue(self.doctor.is_on_vacation)

    def test_set_off_vacation(self):
        self.doctor.is_on_vacation = True
        self.doctor.save()
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.post(
            f"/api/doctors/{self.doctor.id}/set-off-vacation/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "The doctor is not on vacation")
        self.doctor.refresh_from_db()
        self.assertFalse(self.doctor.is_on_vacation)

    def test_set_on_vacation_unauthenticated_returns_403(self):
        response = self.client.post(
            f"/api/doctors/{self.doctor.id}/set-on-vacation/"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_vacation_actions_on_nonexistent_doctor_returns_404(self):
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.post("/api/doctors/999/set-on-vacation/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_appointments_empty(self):
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get(
            f"/api/doctors/{self.doctor.id}/appointments/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_appointment(self):
        self.client.force_authenticate(user=self.doctor_user)
        data = {
            "patient": self.patient.id,
            "appointment_date": "2025-07-01",
            "appointment_time": "10:00:00",
            "notes": "Regular checkup",
            "status": "scheduled",
        }
        response = self.client.post(
            f"/api/doctors/{self.doctor.id}/appointments/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["doctor"], self.doctor.id)
        self.assertEqual(response.data["patient"], self.patient.id)
        self.assertEqual(response.data["status"], "scheduled")

    def test_create_appointment_without_patient_returns_400(self):
        self.client.force_authenticate(user=self.doctor_user)
        data = {
            "appointment_date": "2025-07-01",
            "notes": "No patient specified",
            "status": "scheduled",
        }
        response = self.client.post(
            f"/api/doctors/{self.doctor.id}/appointments/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_unauthenticated_returns_403(self):
        data = {
            "patient": self.patient.id,
            "appointment_date": "2025-07-01",
            "notes": "Regular checkup",
            "status": "scheduled",
        }
        response = self.client.post(
            f"/api/doctors/{self.doctor.id}/appointments/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_appointments_unauthenticated_returns_403(self):
        response = self.client.get(
            f"/api/doctors/{self.doctor.id}/appointments/"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DepartmentViewSetTest(BaseAuthTestCase):
    def test_list_departments(self):
        Department.objects.create(name="Cardiology", description="Heart care")
        Department.objects.create(name="Neurology", description="Brain and nerves")
        response = self.client.get("/api/departments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_departments_empty(self):
        response = self.client.get("/api/departments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_department(self):
        data = {"name": "Cardiology", "description": "Heart and cardiovascular system"}
        response = self.client.post("/api/departments/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 1)
        self.assertEqual(response.data["name"], "Cardiology")

    def test_create_department_without_name_returns_400(self):
        data = {"description": "Heart care"}
        response = self.client.post("/api/departments/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_department(self):
        dept = Department.objects.create(name="Cardiology", description="Heart care")
        response = self.client.get(f"/api/departments/{dept.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Cardiology")
        self.assertEqual(response.data["description"], "Heart care")

    def test_retrieve_nonexistent_department_returns_404(self):
        response = self.client.get("/api/departments/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_department(self):
        dept = Department.objects.create(name="Cardiology", description="Heart care")
        data = {"description": "Updated description"}
        response = self.client.patch(f"/api/departments/{dept.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dept.refresh_from_db()
        self.assertEqual(dept.description, "Updated description")

    def test_delete_department(self):
        dept = Department.objects.create(name="Cardiology", description="Heart care")
        response = self.client.delete(f"/api/departments/{dept.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Department.objects.count(), 0)


class DoctorAvailabilityViewSetTest(BaseAuthTestCase):
    def test_list_availabilities(self):
        DoctorAvailability.objects.create(
            doctor=self.doctor,
            start_date="2025-01-01",
            end_date="2025-12-31",
            start_time="09:00:00",
            end_time="17:00:00",
        )
        response = self.client.get("/api/availabilities/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_availability(self):
        data = {
            "doctor": self.doctor.id,
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "start_time": "09:00:00",
            "end_time": "17:00:00",
        }
        response = self.client.post("/api/availabilities/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DoctorAvailability.objects.count(), 1)

    def test_create_availability_without_doctor_returns_400(self):
        data = {
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "start_time": "09:00:00",
            "end_time": "17:00:00",
        }
        response = self.client.post("/api/availabilities/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_availability(self):
        avail = DoctorAvailability.objects.create(
            doctor=self.doctor,
            start_date="2025-01-01",
            end_date="2025-12-31",
            start_time="09:00:00",
            end_time="17:00:00",
        )
        response = self.client.get(f"/api/availabilities/{avail.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["doctor"], self.doctor.id)

    def test_delete_availability(self):
        avail = DoctorAvailability.objects.create(
            doctor=self.doctor,
            start_date="2025-01-01",
            end_date="2025-12-31",
            start_time="09:00:00",
            end_time="17:00:00",
        )
        response = self.client.delete(f"/api/availabilities/{avail.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class MedicalNoteViewSetTest(BaseAuthTestCase):
    def test_list_notes(self):
        MedicalNote.objects.create(
            doctor=self.doctor,
            note="Patient is recovering",
            date="2025-06-15",
        )
        response = self.client.get("/api/doctor-medical-notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_notes_empty(self):
        response = self.client.get("/api/doctor-medical-notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_note(self):
        data = {
            "doctor": self.doctor.id,
            "note": "Follow-up required",
            "date": "2025-06-20",
        }
        response = self.client.post("/api/doctor-medical-notes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicalNote.objects.count(), 1)
        self.assertEqual(response.data["note"], "Follow-up required")

    def test_create_note_without_doctor_returns_400(self):
        data = {
            "note": "Follow-up required",
            "date": "2025-06-20",
        }
        response = self.client.post("/api/doctor-medical-notes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_note_without_note_field_returns_400(self):
        data = {
            "doctor": self.doctor.id,
            "date": "2025-06-20",
        }
        response = self.client.post("/api/doctor-medical-notes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_note(self):
        note = MedicalNote.objects.create(
            doctor=self.doctor,
            note="Initial consultation",
            date="2025-06-10",
        )
        response = self.client.get(f"/api/doctor-medical-notes/{note.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["note"], "Initial consultation")

    def test_update_note(self):
        note = MedicalNote.objects.create(
            doctor=self.doctor,
            note="Initial consultation",
            date="2025-06-10",
        )
        data = {"note": "Updated note"}
        response = self.client.patch(
            f"/api/doctor-medical-notes/{note.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertEqual(note.note, "Updated note")

    def test_delete_note(self):
        note = MedicalNote.objects.create(
            doctor=self.doctor,
            note="Initial consultation",
            date="2025-06-10",
        )
        response = self.client.delete(f"/api/doctor-medical-notes/{note.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MedicalNote.objects.count(), 0)
