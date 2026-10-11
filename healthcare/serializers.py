from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Doctor, Patient, PatientDoctorMapping

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for user registration via POST /api/auth/register/.
    Requires name, email, and password.
    """

    name = serializers.CharField(
        max_length=150,
        required=True,
        help_text="Full name of the user registering",
    )
    email = serializers.EmailField(
        required=True,
        help_text="Unique email address used for login",
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
        required=True,
        help_text="Strong account password (minimum 8 characters)",
    )

    def validate_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Name cannot be blank.")
        return cleaned

    def validate_email(self, value):
        cleaned = value.strip().lower()
        if (
            User.objects.filter(username__iexact=cleaned).exists()
            or User.objects.filter(email__iexact=cleaned).exists()
        ):
            raise serializers.ValidationError("An account with this email already exists.")
        return cleaned

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        name_parts = validated_data["name"].split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=first_name,
            last_name=last_name,
            password=validated_data["password"],
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication via POST /api/auth/login/.
    Validates email and password, returning authenticated user object.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Registered email address",
    )
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        required=True,
        help_text="Account password",
    )

    def validate(self, attrs):
        email = attrs.get("email", "").strip().lower()
        password = attrs.get("password")

        request = self.context.get("request")
        user = authenticate(request=request, username=email, password=password)

        if not user:
            # Fallback if username differed from email in custom setups
            user_obj = User.objects.filter(email__iexact=email).first()
            if user_obj:
                user = authenticate(request=request, username=user_obj.username, password=password)

        if not user:
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "This account is inactive."})

        attrs["user"] = user
        return attrs


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient CRUD endpoints.
    Owner is tracked automatically from request.user.
    """

    created_by_email = serializers.EmailField(
        source="created_by.email",
        read_only=True,
        help_text="Email of the user who created this patient",
    )

    class Meta:
        model = Patient
        fields = [
            "id",
            "name",
            "age",
            "gender",
            "phone",
            "address",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by_email", "created_at", "updated_at"]

    def validate_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Patient name cannot be blank.")
        return cleaned

    def validate_age(self, value):
        if value < 0 or value > 120:
            raise serializers.ValidationError("Age must be between 0 and 120.")
        return value


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor CRUD endpoints.
    """

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "specialization",
            "email",
            "phone",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Doctor name cannot be blank.")
        return cleaned

    def validate_specialization(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Specialization cannot be blank.")
        return cleaned

    def validate_email(self, value):
        cleaned = value.strip().lower()
        qs = Doctor.objects.filter(email__iexact=cleaned)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return cleaned


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    """
    Serializer for assigning doctors to patients and retrieving mappings.
    Includes rich nested doctor details for GET responses while accepting
    primary keys (patient and doctor IDs) for creation.
    """

    patient_name = serializers.CharField(
        source="patient.name",
        read_only=True,
        help_text="Name of the patient",
    )
    doctor_details = DoctorSerializer(
        source="doctor",
        read_only=True,
        help_text="Full doctor profile information",
    )

    class Meta:
        model = PatientDoctorMapping
        fields = [
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_details",
            "assigned_at",
        ]
        read_only_fields = ["id", "patient_name", "doctor_details", "assigned_at"]

    def validate(self, attrs):
        patient = attrs.get("patient", getattr(self.instance, "patient", None))
        doctor = attrs.get("doctor", getattr(self.instance, "doctor", None))
        request = self.context.get("request")

        # Ensure the authenticated user owns this patient (unless staff)
        if patient and request and not request.user.is_staff:
            if patient.created_by_id != request.user.id:
                raise serializers.ValidationError(
                    {"patient": "You can only assign doctors to patients you created."}
                )

        # Enforce uniqueness constraint check with user-friendly error message
        qs = PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if patient and doctor and qs.exists():
            raise serializers.ValidationError(
                "This doctor is already assigned to this patient."
            )

        return attrs
