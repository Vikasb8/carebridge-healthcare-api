from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Doctor, Patient, PatientDoctorMapping
from .serializers import (
    DoctorSerializer,
    PatientDoctorMappingSerializer,
    PatientSerializer,
)


# ==========================================
# 1. Patient Management Views
# ==========================================

@extend_schema(
    tags=["Patients"],
    summary="List or create patients",
    description="GET: Retrieve all patients created by the authenticated user. POST: Add a new patient record.",
)
class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Patient.objects.all()
        return Patient.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@extend_schema(
    tags=["Patients"],
    summary="Retrieve, update, or delete a patient",
    description="GET: Details of a patient. PUT/PATCH: Update patient details. DELETE: Remove patient record.",
)
class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Patient.objects.all()
        return Patient.objects.filter(created_by=user)


# ==========================================
# 2. Doctor Management Views
# ==========================================

@extend_schema(
    tags=["Doctors"],
    summary="List or create doctors",
    description="GET: Retrieve all doctors in the directory. POST: Add a new doctor (Authenticated users only).",
)
class DoctorListCreateView(generics.ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(
    tags=["Doctors"],
    summary="Retrieve, update, or delete a doctor",
    description="GET: Details of a doctor. PUT/PATCH: Update doctor information. DELETE: Remove doctor record.",
)
class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]


# ==========================================
# 3. Patient-Doctor Mapping Views
# ==========================================

@extend_schema(
    tags=["Mappings"],
    summary="List all mappings or assign doctor to patient",
    description="GET: Retrieve all patient-doctor mappings. POST: Assign a doctor to a patient.",
)
class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return PatientDoctorMapping.objects.all().select_related("patient", "doctor")
        return PatientDoctorMapping.objects.filter(
            patient__created_by=user
        ).select_related("patient", "doctor")

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


@extend_schema(
    tags=["Mappings"],
    summary="Get doctors for a patient OR delete a mapping",
    description=(
        "GET /api/mappings/<patient_id>/ - Retrieve all doctors assigned to a specific patient.\n"
        "DELETE /api/mappings/<id>/ - Remove a doctor mapping by mapping ID (or patient ID)."
    ),
)
class PatientMappingsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="get_doctors_by_patient",
        summary="Get all doctors assigned to a specific patient",
        description="Returns list of doctor assignments for the given patient_id.",
        responses={
            200: PatientDoctorMappingSerializer(many=True),
            404: OpenApiResponse(description="Patient not found or not owned by user"),
        },
    )
    def get(self, request, patient_id):
        user = request.user
        patient_qs = Patient.objects.all() if user.is_staff else Patient.objects.filter(created_by=user)
        patient = patient_qs.filter(pk=patient_id).first()

        if not patient:
            raise NotFound("Patient not found.")

        mappings = (
            PatientDoctorMapping.objects.filter(patient=patient)
            .select_related("doctor", "patient")
        )
        serializer = PatientDoctorMappingSerializer(
            mappings, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="delete_doctor_patient_mapping",
        summary="Remove a doctor from a patient",
        description="Deletes the mapping identified by the mapping ID or patient ID.",
        responses={
            204: OpenApiResponse(description="Doctor successfully unassigned"),
            404: OpenApiResponse(description="Mapping or patient not found"),
        },
    )
    def delete(self, request, patient_id):
        user = request.user

        # 1. Check if the parameter matches a Mapping ID directly
        mapping_qs = PatientDoctorMapping.objects.all() if user.is_staff else PatientDoctorMapping.objects.filter(patient__created_by=user)
        mapping = mapping_qs.filter(pk=patient_id).first()

        # 2. If not found by mapping PK, check if it's a patient ID
        if not mapping:
            doctor_id = request.query_params.get("doctor_id") or request.data.get("doctor") if hasattr(request, "data") else None
            if doctor_id:
                mapping = mapping_qs.filter(patient_id=patient_id, doctor_id=doctor_id).first()
            else:
                # If only one doctor is assigned to this patient, remove that mapping
                single_mappings = mapping_qs.filter(patient_id=patient_id)
                if single_mappings.count() == 1:
                    mapping = single_mappings.first()

        if not mapping:
            raise NotFound("Mapping not found.")

        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
