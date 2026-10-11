from django.urls import path
from .views import (
    DoctorDetailView,
    DoctorListCreateView,
    MappingListCreateView,
    PatientDetailView,
    PatientListCreateView,
    PatientMappingsView,
)

urlpatterns = [
    # Patient Management Endpoints
    path("patients/", PatientListCreateView.as_view(), name="patient-list-create"),
    path("patients/<int:pk>/", PatientDetailView.as_view(), name="patient-detail"),

    # Doctor Management Endpoints
    path("doctors/", DoctorListCreateView.as_view(), name="doctor-list-create"),
    path("doctors/<int:pk>/", DoctorDetailView.as_view(), name="doctor-detail"),

    # Patient-Doctor Mapping Endpoints
    path("mappings/", MappingListCreateView.as_view(), name="mapping-list-create"),
    path("mappings/<int:patient_id>/", PatientMappingsView.as_view(), name="patient-mappings"),
]
