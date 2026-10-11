from django.contrib import admin
from .models import Doctor, Patient, PatientDoctorMapping


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "age", "gender", "phone", "created_by", "created_at")
    list_filter = ("gender", "created_at")
    search_fields = ("name", "phone", "created_by__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "specialization", "email", "phone", "created_at")
    list_filter = ("specialization", "created_at")
    search_fields = ("name", "specialization", "email", "phone")
    readonly_fields = ("created_at", "updated_at")


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "assigned_by", "assigned_at")
    list_filter = ("assigned_at",)
    search_fields = ("patient__name", "doctor__name", "assigned_by__email")
    readonly_fields = ("assigned_at",)
