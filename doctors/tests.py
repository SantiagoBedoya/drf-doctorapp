from datetime import date, time
from django.contrib.auth.models import User, Group
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from doctors.models import Doctor, Department, DoctorAvailability, DoctorReview, MedicalNote
from doctors.serializers import DepartmentSerializer, DoctorAvailabilitySerializer, DoctorReviewSerializer, DoctorSerializer, MedicalNoteSerializer
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

    def test_email_validation_rejects_invalid_format(self):
        data = self.valid_data.copy()
        data["email"] = "invalid-email"
        serializer = DoctorSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_email_validation_error_message(self):
        data = self.valid_data.copy()
        data["email"] = "invalid-email"
        serializer = DoctorSerializer(data=data)
        serializer.is_valid()
        self.assertIn("valid email", str(serializer.errors["email"]).lower())

    def test_email_validation_passes_with_valid_email(self):
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

    def test_contact_number_validation_rejects_non_digits(self):
        data = self.valid_data.copy()
        data["contact_number"] = "abc123"
        serializer = DoctorSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("contact_number", serializer.errors)

    def test_contact_number_validation_passes_with_digits(self):
        data = self.valid_data.copy()
        data["contact_number"] = "1234567"
        serializer = DoctorSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_uses_all_fields(self):
        serializer = DoctorSerializer()
        expected_fields = {
            "id", "first_name", "last_name", "qualification",
            "contact_number", "email", "address", "biography",
            "is_on_vacation", "user",
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
            user=self.doctor_user,
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
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]["first_name"], "John")

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
            "email": "not-an-email",
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

    def test_set_on_vacation_by_other_user_returns_403(self):
        other_user = User.objects.create_user(
            username="other_doctor", password="testpass123"
        )
        other_user.groups.add(Group.objects.get(name="doctors"))
        self.client.force_authenticate(user=other_user)
        response = self.client.post(
            f"/api/doctors/{self.doctor.id}/set-on-vacation/"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_off_vacation_by_other_user_returns_403(self):
        other_user = User.objects.create_user(
            username="other_doctor", password="testpass123"
        )
        other_user.groups.add(Group.objects.get(name="doctors"))
        self.client.force_authenticate(user=other_user)
        self.doctor.is_on_vacation = True
        self.doctor.save()
        response = self.client.post(
            f"/api/doctors/{self.doctor.id}/set-off-vacation/"
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

    def test_create_appointment_by_other_user_returns_403(self):
        other_user = User.objects.create_user(
            username="other_doctor", password="testpass123"
        )
        other_user.groups.add(Group.objects.get(name="doctors"))
        self.client.force_authenticate(user=other_user)
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
        self.assertEqual(len(response.data['results']), 2)

    def test_list_departments_empty(self):
        response = self.client.get("/api/departments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

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
        self.assertEqual(len(response.data['results']), 1)

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
        self.assertEqual(len(response.data['results']), 1)

    def test_list_notes_empty(self):
        response = self.client.get("/api/doctor-medical-notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

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


class DoctorReviewModelTest(TestCase):
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
        self.review = DoctorReview.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            rating=5,
            comment="Excellent doctor",
        )

    def test_review_creation(self):
        review = DoctorReview.objects.get(id=self.review.id)
        self.assertEqual(review.doctor, self.doctor)
        self.assertEqual(review.patient, self.patient)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Excellent doctor")

    def test_review_doctor_relation(self):
        self.assertIn(self.review, self.doctor.reviews.all())

    def test_review_patient_relation(self):
        self.assertIn(self.review, self.patient.doctor_reviews.all())

    def test_unique_together_doctor_patient(self):
        with self.assertRaises(Exception):
            DoctorReview.objects.create(
                doctor=self.doctor,
                patient=self.patient,
                rating=3,
                comment="Duplicate review",
            )

    def test_doctor_cascade_delete(self):
        doctor_id = self.doctor.id
        self.doctor.delete()
        self.assertEqual(DoctorReview.objects.filter(doctor_id=doctor_id).count(), 0)


class DoctorReviewSerializerTest(TestCase):
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

    def test_valid_review_serializer(self):
        data = {
            "doctor": self.doctor.id,
            "patient": self.patient.id,
            "rating": 5,
            "comment": "Great doctor",
        }
        serializer = DoctorReviewSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_rating_below_1_is_invalid(self):
        data = {
            "doctor": self.doctor.id,
            "patient": self.patient.id,
            "rating": 0,
            "comment": "Bad",
        }
        serializer = DoctorReviewSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_rating_above_5_is_invalid(self):
        data = {
            "doctor": self.doctor.id,
            "patient": self.patient.id,
            "rating": 6,
            "comment": "Too high",
        }
        serializer = DoctorReviewSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_rating_1_is_valid(self):
        data = {
            "doctor": self.doctor.id,
            "patient": self.patient.id,
            "rating": 1,
            "comment": "Minimum",
        }
        serializer = DoctorReviewSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_blank_comment_is_valid(self):
        data = {
            "doctor": self.doctor.id,
            "patient": self.patient.id,
            "rating": 3,
            "comment": "",
        }
        serializer = DoctorReviewSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_doctor_is_invalid(self):
        data = {
            "patient": self.patient.id,
            "rating": 4,
            "comment": "No doctor",
        }
        serializer = DoctorReviewSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("doctor", serializer.errors)


class DoctorReviewViewSetTest(BaseAuthTestCase):
    def test_create_review(self):
        data = {
            "doctor": self.doctor.id,
            "patient": self.patient.id,
            "rating": 5,
            "comment": "Excellent doctor",
        }
        response = self.client.post("/api/doctor-reviews/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DoctorReview.objects.count(), 1)
        self.assertEqual(response.data["rating"], 5)

    def test_list_reviews(self):
        DoctorReview.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            rating=4,
            comment="Good doctor",
        )
        response = self.client.get("/api/doctor-reviews/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]["rating"], 4)

    def test_list_reviews_empty(self):
        response = self.client.get("/api/doctor-reviews/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_create_review_invalid_rating_returns_400(self):
        data = {
            "doctor": self.doctor.id,
            "patient": self.patient.id,
            "rating": 10,
            "comment": "Too high",
        }
        response = self.client.post("/api/doctor-reviews/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_missing_doctor_returns_400(self):
        data = {
            "patient": self.patient.id,
            "rating": 4,
            "comment": "No doctor",
        }
        response = self.client.post("/api/doctor-reviews/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_review(self):
        review = DoctorReview.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            rating=3,
            comment="Okay",
        )
        response = self.client.get(f"/api/doctor-reviews/{review.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["comment"], "Okay")

    def test_update_review(self):
        review = DoctorReview.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            rating=2,
            comment="Not great",
        )
        data = {"rating": 4, "comment": "Updated to better"}
        response = self.client.patch(
            f"/api/doctor-reviews/{review.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, "Updated to better")

    def test_delete_review(self):
        review = DoctorReview.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            rating=3,
            comment="Okay",
        )
        response = self.client.delete(f"/api/doctor-reviews/{review.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DoctorReview.objects.count(), 0)

    def test_duplicate_review_returns_400(self):
        DoctorReview.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            rating=5,
            comment="First review",
        )
        data = {
            "doctor": self.doctor.id,
            "patient": self.patient.id,
            "rating": 3,
            "comment": "Second review",
        }
        response = self.client.post("/api/doctor-reviews/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
