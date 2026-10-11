from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Doctor, Patient, PatientDoctorMapping

User = get_user_model()


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class HealthcareAPITests(APITestCase):
    """
    Comprehensive test suite covering Authentication, Patient Management,
    Doctor Management, and Patient-Doctor Mapping APIs.
    """

    def setUp(self):
        self.user_a = User.objects.create_user(
            username="doctor_staff@example.com",
            email="doctor_staff@example.com",
            password="StrongPass123!",
            first_name="Alice",
            last_name="Staff",
        )
        self.user_b = User.objects.create_user(
            username="other_user@example.com",
            email="other_user@example.com",
            password="StrongPass123!",
            first_name="Bob",
            last_name="Other",
        )

        # Authenticate client as user_a by default
        self.client.force_authenticate(user=self.user_a)

    # -------------------------------------------------------------
    # 1. Authentication Tests
    # -------------------------------------------------------------

    def test_register_success(self):
        self.client.force_authenticate(user=None)
        payload = {
            "name": "Dr. Sarah Connor",
            "email": "sarah.connor@example.com",
            "password": "SecurePassword987!",
        }
        res = self.client.post("/api/auth/register/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["user"]["email"], "sarah.connor@example.com")
        self.assertEqual(res.data["user"]["name"], "Dr. Sarah Connor")

    def test_register_duplicate_email(self):
        self.client.force_authenticate(user=None)
        payload = {
            "name": "Duplicate User",
            "email": "doctor_staff@example.com",  # Already exists in setUp
            "password": "SecurePassword987!",
        }
        res = self.client.post("/api/auth/register/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_data(self):
        self.client.force_authenticate(user=None)
        # Empty name and weak password
        payload = {"name": "", "email": "invalid-email", "password": "123"}
        res = self.client.post("/api/auth/register/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        self.client.force_authenticate(user=None)
        payload = {
            "email": "doctor_staff@example.com",
            "password": "StrongPass123!",
        }
        res = self.client.post("/api/auth/login/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.data["user"]["email"], "doctor_staff@example.com")

    def test_login_invalid_credentials(self):
        self.client.force_authenticate(user=None)
        payload = {
            "email": "doctor_staff@example.com",
            "password": "WrongPassword!",
        }
        res = self.client.post("/api/auth/login/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------
    # 2. Authentication Requirement on Protected Endpoints
    # -------------------------------------------------------------

    def test_unauthenticated_requests_blocked(self):
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get("/api/patients/").status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.post("/api/patients/", {}).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get("/api/doctors/").status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.post("/api/doctors/", {}).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get("/api/mappings/").status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.post("/api/mappings/", {}).status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------------------------------------------------
    # 3. Patient Management Tests
    # -------------------------------------------------------------

    def test_patient_crud_and_isolation(self):
        # 1. Create Patient
        patient_data = {
            "name": "Jane Doe",
            "age": 34,
            "gender": "Female",
            "phone": "+1234567890",
            "address": "123 Elm Street, City",
        }
        create_res = self.client.post("/api/patients/", patient_data, format="json")
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        patient_id = create_res.data["id"]
        self.assertEqual(create_res.data["name"], "Jane Doe")

        # 2. List Patients (should include Jane Doe)
        list_res = self.client.get("/api/patients/")
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 1)

        # 3. Retrieve Patient Detail
        detail_res = self.client.get(f"/api/patients/{patient_id}/")
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_res.data["age"], 34)

        # 4. Update Patient (PUT)
        update_data = {
            "name": "Jane Doe Updated",
            "age": 35,
            "gender": "Female",
            "phone": "+1234567899",
            "address": "456 Oak Avenue",
        }
        put_res = self.client.put(f"/api/patients/{patient_id}/", update_data, format="json")
        self.assertEqual(put_res.status_code, status.HTTP_200_OK)
        self.assertEqual(put_res.data["name"], "Jane Doe Updated")
        self.assertEqual(put_res.data["age"], 35)

        # 5. Isolation: user_b should not see or be able to access Jane Doe
        self.client.force_authenticate(user=self.user_b)
        b_list = self.client.get("/api/patients/")
        self.assertEqual(len(b_list.data), 0)
        b_detail = self.client.get(f"/api/patients/{patient_id}/")
        self.assertEqual(b_detail.status_code, status.HTTP_404_NOT_FOUND)

        # Switch back to user_a and delete
        self.client.force_authenticate(user=self.user_a)
        del_res = self.client.delete(f"/api/patients/{patient_id}/")
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(f"/api/patients/{patient_id}/").status_code, status.HTTP_404_NOT_FOUND)

    def test_patient_validation(self):
        # Invalid age (> 120)
        invalid_res = self.client.post(
            "/api/patients/",
            {"name": "Old Patient", "age": 150, "gender": "Male"},
            format="json",
        )
        self.assertEqual(invalid_res.status_code, status.HTTP_400_BAD_REQUEST)

        # Blank name
        blank_name_res = self.client.post(
            "/api/patients/",
            {"name": "   ", "age": 25, "gender": "Female"},
            format="json",
        )
        self.assertEqual(blank_name_res.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------
    # 4. Doctor Management Tests
    # -------------------------------------------------------------

    def test_doctor_crud(self):
        # 1. Create Doctor
        doc_data = {
            "name": "Dr. Gregory House",
            "specialization": "Diagnostic Medicine",
            "email": "dr.house@princetonplainsboro.org",
            "phone": "+1987654321",
        }
        create_res = self.client.post("/api/doctors/", doc_data, format="json")
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        doctor_id = create_res.data["id"]

        # 2. List Doctors
        list_res = self.client.get("/api/doctors/")
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 1)

        # 3. Retrieve Doctor Detail
        detail_res = self.client.get(f"/api/doctors/{doctor_id}/")
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_res.data["name"], "Dr. Gregory House")

        # 4. Update Doctor (PUT)
        update_data = {
            "name": "Dr. Gregory House, M.D.",
            "specialization": "Nephrology & Pathology",
            "email": "dr.house@princetonplainsboro.org",
            "phone": "+1987654329",
        }
        put_res = self.client.put(f"/api/doctors/{doctor_id}/", update_data, format="json")
        self.assertEqual(put_res.status_code, status.HTTP_200_OK)
        self.assertEqual(put_res.data["name"], "Dr. Gregory House, M.D.")

        # 5. Delete Doctor
        del_res = self.client.delete(f"/api/doctors/{doctor_id}/")
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(f"/api/doctors/{doctor_id}/").status_code, status.HTTP_404_NOT_FOUND)

    def test_doctor_duplicate_email(self):
        doc_data = {
            "name": "Dr. Robert Chase",
            "specialization": "Cardiology",
            "email": "chase@hospital.org",
        }
        res1 = self.client.post("/api/doctors/", doc_data, format="json")
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        res2 = self.client.post("/api/doctors/", doc_data, format="json")
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------
    # 5. Patient-Doctor Mapping Tests
    # -------------------------------------------------------------

    def test_mapping_assignment_and_operations(self):
        # Create a patient for user_a
        patient = Patient.objects.create(
            name="John Miller",
            age=45,
            gender="Male",
            created_by=self.user_a,
        )

        # Create a patient for user_b
        patient_b = Patient.objects.create(
            name="Bob's Patient",
            age=22,
            gender="Other",
            created_by=self.user_b,
        )

        # Create doctors
        doc1 = Doctor.objects.create(
            name="Dr. Allison Cameron",
            specialization="Immunology",
            email="cameron@hospital.org",
        )
        doc2 = Doctor.objects.create(
            name="Dr. Eric Foreman",
            specialization="Neurology",
            email="foreman@hospital.org",
        )

        # 1. Assign doc1 to patient (User A owns patient)
        assign_data = {"patient": patient.id, "doctor": doc1.id}
        assign_res = self.client.post("/api/mappings/", assign_data, format="json")
        self.assertEqual(assign_res.status_code, status.HTTP_201_CREATED)
        mapping_id = assign_res.data["id"]

        # 2. User A cannot assign a doctor to patient_b (owned by User B)
        unauthorized_assign = self.client.post(
            "/api/mappings/",
            {"patient": patient_b.id, "doctor": doc2.id},
            format="json",
        )
        self.assertEqual(unauthorized_assign.status_code, status.HTTP_400_BAD_REQUEST)

        # 3. Duplicate assignment prevented
        duplicate_res = self.client.post("/api/mappings/", assign_data, format="json")
        self.assertEqual(duplicate_res.status_code, status.HTTP_400_BAD_REQUEST)

        # 4. List all mappings for user_a
        list_res = self.client.get("/api/mappings/")
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 1)
        self.assertEqual(list_res.data[0]["doctor_details"]["name"], "Dr. Allison Cameron")

        # 5. Get all doctors assigned to a specific patient: GET /api/mappings/<patient_id>/
        patient_mappings_res = self.client.get(f"/api/mappings/{patient.id}/")
        self.assertEqual(patient_mappings_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(patient_mappings_res.data), 1)
        self.assertEqual(patient_mappings_res.data[0]["doctor_details"]["specialization"], "Immunology")

        # 6. Delete mapping by mapping ID: DELETE /api/mappings/<id>/
        del_mapping_res = self.client.delete(f"/api/mappings/{mapping_id}/")
        self.assertEqual(del_mapping_res.status_code, status.HTTP_204_NO_CONTENT)

        # Verify mapping is deleted
        check_res = self.client.get(f"/api/mappings/{patient.id}/")
        self.assertEqual(len(check_res.data), 0)

    # -------------------------------------------------------------
    # 6. Swagger API Documentation Schema
    # -------------------------------------------------------------

    def test_swagger_schema_accessible(self):
        res = self.client.get("/api/schema/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
