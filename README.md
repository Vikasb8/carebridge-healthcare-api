# CareBridge Healthcare REST API

A secure, scalable backend system for a healthcare application built with **Django**, **Django REST Framework (DRF)**, **SimpleJWT**, and **PostgreSQL**.

---

## 🚀 Features

- **Zero-Config Setup**: Runs out-of-the-box with standard defaults without needing a `.env` file.
- **PostgreSQL Ready**: Production-ready database support using environment variables or settings.
- **JWT Authentication**: User registration and login using JSON Web Tokens (`djangorestframework-simplejwt`), with password validation and case-insensitive email uniqueness.
- **Patient Management**: Full CRUD operations with patient records strictly scoped to their creator.
- **Doctor Directory**: Full CRUD management of medical practitioners and their specializations.
- **Patient-Doctor Mapping**: Assign doctors to patients with database-level uniqueness constraints and ownership enforcement.
- **Error Handling & Validation**: Centralized custom exception handler returning consistent `{"error": ...}` responses.
- **Interactive Documentation**: Auto-generated Swagger UI (`/api/docs/`) and ReDoc (`/api/redoc/`) powered by `drf-spectacular`.
- **Automated Test Suite**: 12 comprehensive unit and integration tests passing in under 0.2 seconds (`python manage.py test`).
- **Postman Collection**: Ready-to-import Postman collection with test scripts that automatically capture JWT tokens and IDs.

---

## 🛠 Tech Stack

- **Framework**: Django 5.1+ & Django REST Framework 3.15+
- **Authentication**: `djangorestframework-simplejwt`
- **Database**: PostgreSQL / SQLite (zero-config default)
- **Database Driver**: `psycopg` (v3)
- **API Documentation**: `drf-spectacular` (OpenAPI 3.0 & Swagger UI)

---

## 📁 Project Structure

```text
carebridge-healthcare-api/
├── config/
│   ├── settings.py           # Django settings, DB & SimpleJWT config
│   ├── urls.py               # Root URL configuration & Swagger routes
│   ├── wsgi.py
│   └── asgi.py
├── healthcare/
│   ├── models.py             # Patient, Doctor, PatientDoctorMapping models
│   ├── serializers.py        # DRF ModelSerializers with validation
│   ├── views.py              # Patient, Doctor, and Mapping API views
│   ├── auth_views.py         # Register and Login API views
│   ├── urls.py               # Core API routes (/api/patients/, /api/doctors/, /api/mappings/)
│   ├── auth_urls.py          # Auth API routes (/api/auth/register/, /api/auth/login/)
│   ├── exceptions.py         # Custom centralized exception handler
│   ├── admin.py              # Django Admin site customization
│   ├── tests.py              # Comprehensive test suite (12 tests)
│   └── migrations/           # Database migrations
│       └── 0001_initial.py
├── postman/
│   └── CareBridge.postman_collection.json # Ready-to-import Postman suite
├── manage.py
└── requirements.txt
```

---

## ⚙️ Quick Start (No `.env` Needed!)

### 1. Install Dependencies
```powershell
# In PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
*(Or in Bash: `source .venv/bin/activate && pip install -r requirements.txt`)*

### 2. Run Migrations & Start Server
```powershell
python manage.py migrate
python manage.py runserver
```

- **Base URL**: `http://127.0.0.1:8000`
- **Swagger Documentation**: `http://127.0.0.1:8000/api/docs/`
- **ReDoc Documentation**: `http://127.0.0.1:8000/api/redoc/`
- **Django Admin**: `http://127.0.0.1:8000/admin/`

---

## 🐘 Optional: Using PostgreSQL

To connect to a PostgreSQL database, simply provide your PostgreSQL environment variables:
```powershell
$env:DB_ENGINE="django.db.backends.postgresql"
$env:DB_NAME="carebridge_db"
$env:DB_USER="carebridge_user"
$env:DB_PASSWORD="your_password"
$env:DB_HOST="127.0.0.1"
$env:DB_PORT="5432"

python manage.py migrate
python manage.py runserver
```

---

## 🧪 Running Automated Tests

Run the full test suite anytime with:
```powershell
python manage.py test
```

---

## 📡 API Reference

All protected routes require the HTTP header:
```http
Authorization: Bearer <your_access_token>
```

### 1. Authentication APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register new user with `name`, `email`, and `password` | ❌ No |
| `POST` | `/api/auth/login/` | Log in and receive JWT `access` and `refresh` tokens | ❌ No |
| `POST` | `/api/auth/token/refresh/` | Refresh expired access token | ❌ No |

### 2. Patient Management APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/patients/` | Add a new patient record | ✅ Yes |
| `GET` | `/api/patients/` | Retrieve all patients created by the authenticated user | ✅ Yes |
| `GET` | `/api/patients/<id>/` | Get details of a specific patient | ✅ Yes |
| `PUT` | `/api/patients/<id>/` | Update all patient details | ✅ Yes |
| `PATCH`| `/api/patients/<id>/` | Partial update of patient details | ✅ Yes |
| `DELETE`| `/api/patients/<id>/` | Delete a patient record | ✅ Yes |

### 3. Doctor Management APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/doctors/` | Add a new doctor record | ✅ Yes |
| `GET` | `/api/doctors/` | Retrieve all doctors | ✅ Yes |
| `GET` | `/api/doctors/<id>/` | Get details of a specific doctor | ✅ Yes |
| `PUT` | `/api/doctors/<id>/` | Update doctor details | ✅ Yes |
| `PATCH`| `/api/doctors/<id>/` | Partial update of doctor details | ✅ Yes |
| `DELETE`| `/api/doctors/<id>/` | Delete a doctor record | ✅ Yes |

### 4. Patient-Doctor Mapping APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/mappings/` | Assign a doctor to a patient (`patient`, `doctor`) | ✅ Yes |
| `GET` | `/api/mappings/` | Retrieve all patient-doctor mappings | ✅ Yes |
| `GET` | `/api/mappings/<patient_id>/` | Get all doctors assigned to a specific patient | ✅ Yes |
| `DELETE`| `/api/mappings/<id>/` | Remove a doctor from a patient (by mapping ID or patient ID) | ✅ Yes |

---

## 📮 Postman Collection

Import [postman/CareBridge.postman_collection.json](file:///d:/downloads/carebridge-healthcare-api/postman/CareBridge.postman_collection.json) into Postman. It contains pre-configured requests for all 16 endpoints with test scripts that automatically save tokens and IDs for end-to-end testing.
