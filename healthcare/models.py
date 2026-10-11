from django.conf import settings
from django.db import models


class Patient(models.Model):
    """
    Patient model representing a patient registered by a healthcare user.
    Records are isolated so users only access patients they created.
    """

    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"
        OTHER = "Other", "Other"
        PREFER_NOT_TO_SAY = "Prefer not to say", "Prefer not to say"

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patients",
        help_text="User who registered this patient record",
    )
    name = models.CharField(max_length=120, help_text="Full name of the patient")
    age = models.PositiveSmallIntegerField(help_text="Age in years (0 - 120)")
    gender = models.CharField(max_length=24, choices=Gender.choices)
    phone = models.CharField(max_length=20, blank=True, help_text="Contact phone number")
    address = models.TextField(blank=True, help_text="Residential or mailing address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

    def __str__(self):
        return f"{self.name} (Patient #{self.pk})"


class Doctor(models.Model):
    """
    Doctor model representing a medical practitioner in the healthcare network.
    """

    name = models.CharField(max_length=120, help_text="Doctor's full name with title")
    specialization = models.CharField(max_length=120, help_text="Medical specialty (e.g., Cardiology)")
    email = models.EmailField(unique=True, help_text="Professional email address (unique)")
    phone = models.CharField(max_length=20, blank=True, help_text="Contact telephone number")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"

    def __str__(self):
        return f"{self.name} — {self.specialization}"


class PatientDoctorMapping(models.Model):
    """
    Relationship mapping assigning a doctor to a patient.
    Enforces a unique constraint to prevent duplicate doctor assignments to the same patient.
    """

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="doctor_mappings",
        help_text="The patient receiving medical care",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="patient_mappings",
        help_text="The doctor assigned to the patient",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_mappings",
        help_text="User who made this assignment",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "doctor"],
                name="unique_patient_doctor_assignment",
            )
        ]
        ordering = ["-assigned_at"]
        verbose_name = "Patient-Doctor Mapping"
        verbose_name_plural = "Patient-Doctor Mappings"

    def __str__(self):
        return f"Patient #{self.patient_id} ({self.patient.name}) -> Doctor #{self.doctor_id} ({self.doctor.name})"
