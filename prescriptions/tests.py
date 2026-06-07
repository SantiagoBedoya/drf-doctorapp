from datetime import date, timedelta
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from doctors.models import Doctor
from patients.models import Patient
from prescriptions.models import Medication, Prescription, PrescriptionStatus
from prescriptions.serializers import MedicationSerializer, PrescriptionSerializer


class MedicationModelTest(TestCase):
    def setUp(self):
        self.medication = Medication.objects.create(
            name="Amoxicillin",
            description="Antibiotic used to treat bacterial infections",
            side_effects="Nausea, diarrhea",
            contraindications="Allergy to penicillin",
        )

    def test_medication_creation(self):
        medication = Medication.objects.get(id=self.medication.id)
        self.assertEqual(medication.name, "Amoxicillin")
        self.assertEqual(medication.side_effects, "Nausea, diarrhea")

    def test_medication_default_blank_fields(self):
        medication = Medication.objects.create(
            name="Ibuprofen",
            description="Pain reliever",
        )
        self.assertEqual(medication.side_effects, "")
        self.assertEqual(medication.contraindications, "")

    def test_medication_str(self):
        self.assertEqual(str(self.medication), "Amoxicillin")

    def test_medication_ordering(self):
        Medication.objects.create(name="Zyrtec", description="Antihistamine")
        Medication.objects.create(name="Benzonatate", description="Cough suppressant")
        names = [m.name for m in Medication.objects.all()]
        self.assertEqual(names, sorted(names))


class PrescriptionModelTest(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name="John", last_name="Doe", qualification="MD",
            contact_number="1234567890", email="john@example.com",
            address="123 Main St", biography="Cardiologist",
        )
        self.patient = Patient.objects.create(
            first_name="Jane", last_name="Patient",
            date_of_birth="1990-01-01", contact_number="0987654321",
            email="jane@example.com", address="456 Oak Ave",
            medical_history="None",
        )
        self.medication = Medication.objects.create(
            name="Amoxicillin", description="Antibiotic",
        )
        self.future_date = date.today() + timedelta(days=5)
        self.prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            medication=self.medication,
            dosage="500mg",
            frequency="Twice daily",
            duration="7 days",
            start_date=self.future_date,
            notes="Take with food",
        )

    def test_prescription_creation(self):
        p = Prescription.objects.get(id=self.prescription.id)
        self.assertEqual(p.dosage, "500mg")
        self.assertEqual(p.frequency, "Twice daily")
        self.assertEqual(p.duration, "7 days")
        self.assertEqual(p.notes, "Take with food")
        self.assertEqual(p.status, PrescriptionStatus.ACTIVE)

    def test_prescription_default_status(self):
        p = Prescription.objects.create(
            patient=self.patient, doctor=self.doctor,
            medication=self.medication, dosage="250mg",
            frequency="Once daily", duration="5 days",
            start_date=self.future_date,
        )
        self.assertEqual(p.status, PrescriptionStatus.ACTIVE)

    def test_prescription_patient_relation(self):
        self.assertIn(self.prescription, self.patient.prescriptions.all())

    def test_prescription_doctor_relation(self):
        self.assertIn(self.prescription, self.doctor.prescriptions.all())

    def test_prescription_medication_relation(self):
        self.assertIn(self.prescription, self.medication.prescriptions.all())

    def test_doctor_cascade_delete(self):
        doctor_id = self.doctor.id
        self.doctor.delete()
        self.assertEqual(Prescription.objects.filter(doctor_id=doctor_id).count(), 0)

    def test_patient_cascade_delete(self):
        patient_id = self.patient.id
        self.patient.delete()
        self.assertEqual(Prescription.objects.filter(patient_id=patient_id).count(), 0)

    def test_medication_cascade_delete(self):
        med_id = self.medication.id
        self.medication.delete()
        self.assertEqual(Prescription.objects.filter(medication_id=med_id).count(), 0)


class MedicationSerializerTest(TestCase):
    def setUp(self):
        self.medication = Medication.objects.create(
            name="Ibuprofen", description="Pain reliever",
        )

    def test_valid_serializer(self):
        data = {"name": "Paracetamol", "description": "Fever reducer"}
        serializer = MedicationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_name_is_invalid(self):
        data = {"description": "Some description"}
        serializer = MedicationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_missing_description_is_invalid(self):
        data = {"name": "TestMed"}
        serializer = MedicationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)

    def test_serializer_fields(self):
        serializer = MedicationSerializer()
        expected = {"id", "name", "description", "side_effects", "contraindications", "created_at"}
        self.assertEqual(set(serializer.fields.keys()), expected)


class PrescriptionSerializerTest(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name="John", last_name="Doe", qualification="MD",
            contact_number="1234567890", email="john@example.com",
            address="123 Main St", biography="Cardiologist",
        )
        self.patient = Patient.objects.create(
            first_name="Jane", last_name="Patient",
            date_of_birth="1990-01-01", contact_number="0987654321",
            email="jane@example.com", address="456 Oak Ave",
            medical_history="None",
        )
        self.medication = Medication.objects.create(
            name="Amoxicillin", description="Antibiotic",
        )
        self.future_date = (date.today() + timedelta(days=5)).isoformat()

    def test_valid_serializer(self):
        data = {
            "patient": self.patient.id,
            "doctor": self.doctor.id,
            "medication": self.medication.id,
            "dosage": "500mg",
            "frequency": "Twice daily",
            "duration": "7 days",
            "start_date": self.future_date,
        }
        serializer = PrescriptionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_patient_is_invalid(self):
        data = {
            "doctor": self.doctor.id,
            "medication": self.medication.id,
            "dosage": "500mg",
            "frequency": "Twice daily",
            "duration": "7 days",
            "start_date": self.future_date,
        }
        serializer = PrescriptionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("patient", serializer.errors)

    def test_missing_doctor_is_invalid(self):
        data = {
            "patient": self.patient.id,
            "medication": self.medication.id,
            "dosage": "500mg",
            "frequency": "Twice daily",
            "duration": "7 days",
            "start_date": self.future_date,
        }
        serializer = PrescriptionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("doctor", serializer.errors)

    def test_serializer_fields(self):
        serializer = PrescriptionSerializer()
        expected = {
            "id", "patient", "doctor", "appointment", "medication",
            "dosage", "frequency", "duration", "start_date", "end_date",
            "notes", "status", "prescribed_at", "updated_at",
        }
        self.assertEqual(set(serializer.fields.keys()), expected)


class MedicationViewSetTest(APITestCase):
    def setUp(self):
        self.med1 = Medication.objects.create(name="Amoxicillin", description="Antibiotic")
        self.med2 = Medication.objects.create(name="Ibuprofen", description="Pain reliever")

    def test_list_medications(self):
        response = self.client.get("/api/medications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_create_medication(self):
        data = {"name": "Paracetamol", "description": "Fever reducer"}
        response = self.client.post("/api/medications/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Medication.objects.count(), 3)

    def test_retrieve_medication(self):
        response = self.client.get("/api/medications/{0}/".format(self.med1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Amoxicillin")

    def test_retrieve_nonexistent_returns_404(self):
        response = self.client.get("/api/medications/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_medication(self):
        response = self.client.patch(
            "/api/medications/{0}/".format(self.med1.id),
            {"description": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "Updated")

    def test_delete_medication(self):
        response = self.client.delete("/api/medications/{0}/".format(self.med1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Medication.objects.count(), 1)


class PrescriptionViewSetTest(APITestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            first_name="John", last_name="Doe", qualification="MD",
            contact_number="1234567890", email="john@example.com",
            address="123 Main St", biography="Cardiologist",
        )
        self.patient = Patient.objects.create(
            first_name="Jane", last_name="Patient",
            date_of_birth="1990-01-01", contact_number="0987654321",
            email="jane@example.com", address="456 Oak Ave",
            medical_history="None",
        )
        self.medication = Medication.objects.create(
            name="Amoxicillin", description="Antibiotic",
        )
        self.future_date = (date.today() + timedelta(days=5)).isoformat()
        self.valid_data = {
            "patient": self.patient.id,
            "doctor": self.doctor.id,
            "medication": self.medication.id,
            "dosage": "500mg",
            "frequency": "Twice daily",
            "duration": "7 days",
            "start_date": self.future_date,
            "notes": "Take with food",
        }

    def test_list_prescriptions_empty(self):
        response = self.client.get("/api/prescriptions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_create_prescription(self):
        response = self.client.post("/api/prescriptions/", self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Prescription.objects.count(), 1)
        self.assertEqual(response.data["dosage"], "500mg")
        self.assertEqual(response.data["status"], "active")

    def test_list_prescriptions(self):
        self.client.post("/api/prescriptions/", self.valid_data, format="json")
        response = self.client.get("/api/prescriptions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_prescription(self):
        response = self.client.post("/api/prescriptions/", self.valid_data, format="json")
        presc_id = response.data["id"]
        response = self.client.get("/api/prescriptions/{0}/".format(presc_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["dosage"], "500mg")

    def test_retrieve_nonexistent_prescription_returns_404(self):
        response = self.client.get("/api/prescriptions/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_prescription(self):
        response = self.client.post("/api/prescriptions/", self.valid_data, format="json")
        presc_id = response.data["id"]
        updated = self.valid_data.copy()
        updated["dosage"] = "1000mg"
        response = self.client.put(
            "/api/prescriptions/{0}/".format(presc_id), updated, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["dosage"], "1000mg")

    def test_partial_update_prescription(self):
        response = self.client.post("/api/prescriptions/", self.valid_data, format="json")
        presc_id = response.data["id"]
        response = self.client.patch(
            "/api/prescriptions/{0}/".format(presc_id),
            {"notes": "Updated notes"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["notes"], "Updated notes")

    def test_delete_prescription(self):
        response = self.client.post("/api/prescriptions/", self.valid_data, format="json")
        presc_id = response.data["id"]
        response = self.client.delete("/api/prescriptions/{0}/".format(presc_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Prescription.objects.count(), 0)

    def test_create_with_invalid_patient_returns_400(self):
        data = self.valid_data.copy()
        data["patient"] = 999
        response = self.client.post("/api/prescriptions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_invalid_doctor_returns_400(self):
        data = self.valid_data.copy()
        data["doctor"] = 999
        response = self.client.post("/api/prescriptions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_invalid_medication_returns_400(self):
        data = self.valid_data.copy()
        data["medication"] = 999
        response = self.client.post("/api/prescriptions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
