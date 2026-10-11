from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from healthcare.models import Doctor, Patient, PatientDoctorMapping

User = get_user_model()


class Command(BaseCommand):
    help = "Populate database with sample healthcare data (doctors, patients, and mappings)."

    def handle(self, *args, **options):
        # 1. Ensure a default demo user exists
        demo_user, created = User.objects.get_or_create(
            username="admin@carebridge.org",
            defaults={
                "email": "admin@carebridge.org",
                "first_name": "Admin",
                "last_name": "CareBridge",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            demo_user.set_password("admin123")
            demo_user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user: admin@carebridge.org / admin123"))

        # 2. Seed Sample Doctors
        doctors_data = [
            {
                "name": "Dr. Sarah Connor, M.D.",
                "specialization": "Cardiology",
                "email": "sarah.connor@hospital.org",
                "phone": "+1-555-0101",
            },
            {
                "name": "Dr. Gregory House, M.D.",
                "specialization": "Diagnostic Medicine",
                "email": "gregory.house@hospital.org",
                "phone": "+1-555-0102",
            },
            {
                "name": "Dr. Allison Cameron, M.D.",
                "specialization": "Immunology",
                "email": "allison.cameron@hospital.org",
                "phone": "+1-555-0103",
            },
            {
                "name": "Dr. Eric Foreman, M.D.",
                "specialization": "Neurology",
                "email": "eric.foreman@hospital.org",
                "phone": "+1-555-0104",
            },
            {
                "name": "Dr. Robert Chase, M.D.",
                "specialization": "Intensive Care",
                "email": "robert.chase@hospital.org",
                "phone": "+1-555-0105",
            },
        ]

        created_doctors = []
        for data in doctors_data:
            doc, _ = Doctor.objects.get_or_create(email=data["email"], defaults=data)
            created_doctors.append(doc)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_doctors)} doctors."))

        # 3. Seed Sample Patients
        patients_data = [
            {
                "name": "Ananya Rao",
                "age": 28,
                "gender": "Female",
                "phone": "+91-9876543210",
                "address": "14 Residency Road, Bengaluru, Karnataka",
                "created_by": demo_user,
            },
            {
                "name": "Rahul Verma",
                "age": 45,
                "gender": "Male",
                "phone": "+91-9876543211",
                "address": "22 Park Street, Kolkata, West Bengal",
                "created_by": demo_user,
            },
            {
                "name": "Priya Nair",
                "age": 34,
                "gender": "Female",
                "phone": "+91-9876543212",
                "address": "8 Marina Beach Road, Chennai, Tamil Nadu",
                "created_by": demo_user,
            },
            {
                "name": "David Miller",
                "age": 62,
                "gender": "Male",
                "phone": "+1-555-0201",
                "address": "742 Evergreen Terrace, Springfield",
                "created_by": demo_user,
            },
        ]

        created_patients = []
        for data in patients_data:
            patient, _ = Patient.objects.get_or_create(
                name=data["name"],
                created_by=data["created_by"],
                defaults=data,
            )
            created_patients.append(patient)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_patients)} patients."))

        # 4. Seed Sample Patient-Doctor Mappings
        mappings_data = [
            (created_patients[0], created_doctors[0]),  # Ananya -> Dr. Sarah Connor (Cardiology)
            (created_patients[0], created_doctors[2]),  # Ananya -> Dr. Allison Cameron (Immunology)
            (created_patients[1], created_doctors[1]),  # Rahul -> Dr. Gregory House (Diagnostics)
            (created_patients[2], created_doctors[3]),  # Priya -> Dr. Eric Foreman (Neurology)
            (created_patients[3], created_doctors[0]),  # David -> Dr. Sarah Connor (Cardiology)
        ]

        mapping_count = 0
        for patient, doctor in mappings_data:
            _, created = PatientDoctorMapping.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                defaults={"assigned_by": demo_user},
            )
            if created:
                mapping_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Seeded {mapping_count} patient-doctor mappings.")
        )
        self.stdout.write(
            self.style.SUCCESS("Healthcare demo data seeding complete!")
        )
