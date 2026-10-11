# CareBridge Healthcare REST API

A secure, scalable backend system for a healthcare application built with **Django**, **Django REST Framework (DRF)**, **SimpleJWT**, and **PostgreSQL**.

---

## 🚀 Features

- **JWT Authentication**: User registration and login with JSON Web Tokens (`djangorestframework-simplejwt`), with password validation and case-insensitive email uniqueness.
- **Patient Management**: Full CRUD operations with patient records strictly scoped to their creator.
- **Doctor Directory**: Full CRUD management of medical practitioners and their specializations.
- **Patient-Doctor Mapping**: Assign doctors to patients with database-level uniqueness constraints and ownership enforcement.
- **PostgreSQL Ready**: Production-ready database configuration using environment variables and `psycopg3`.
- **Error Handling & Validation**: Centralized custom exception handler returning consistent, user-friendly error responses.
- **Interactive Documentation**: Auto-generated Swagger UI and ReDoc powered by `drf-spectacular`.
- **Comprehensive Automated Tests**: 100% test coverage across authentication, authorization, CRUD, and relational mapping.
- **Postman Collection**: Ready-to-import Postman collection with test scripts that automatically capture JWT tokens and IDs.

---

## 🛠 Tech Stack

- **Framework**: Django 5.1+ & Django REST Framework 3.15+
- **Authentication**: `djangorestframework-simplejwt`
- **Database**: PostgreSQL (with in-memory SQLite runner for zero-dependency test execution)
- **Database Driver**: `psycopg` (v3)
- **API Documentation**: `drf-spectacular` (Swagger & OpenAPI 3.0)
- **Configuration**: `python-dotenv`

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
│   ├── tests.py              # Comprehensive test suite
│   └── migrations/           # Database migration files
├── postman/
│   └── CareBridge.postman_collection.json # Ready-to-import Postman suite
├── .env.example              # Environment variables template
├── manage.py
└── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1. Clone & Set Up Virtual Environment

**Windows PowerShell:**
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

Ensure your PostgreSQL credentials in `.env` match your local PostgreSQL service:
```ini
DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=django.db.backends.postgresql
DB_NAME=carebridge_db
DB_USER=carebridge_user
DB_PASSWORD=your_postgres_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

*(Note: For instant local testing without a live PostgreSQL instance, set `DB_ENGINE=django.db.backends.sqlite3`)*

### 3. Create Database & Run Migrations

In PostgreSQL (`psql`):
```sql
CREATE DATABASE carebridge_db;
CREATE USER carebridge_user WITH PASSWORD 'your_postgres_password';
GRANT ALL PRIVILEGES ON DATABASE carebridge_db TO carebridge_user;
```

Run Django migrations:
```powershell
python manage.py migrate
```

### 4. Create Superuser (Optional for Django Admin)
```powershell
python manage.py createsuperuser
```

### 5. Run Development Server
```powershell
python manage.py runserver
```

- **Base URL**: `http://127.0.0.1:8000`
- **Swagger Documentation**: `http://127.0.0.1:8000/api/docs/`
- **ReDoc Documentation**: `http://127.0.0.1:8000/api/redoc/`
- **Django Admin**: `http://127.0.0.1:8000/admin/`

---

## 🧪 Running Automated Tests

Run the full automated test suite:
```powershell
python manage.py test
```

The test runner utilizes an in-memory SQLite database for high-speed, isolated execution without touching your persistent PostgreSQL database.

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

#### Example: Register User
```json
POST /api/auth/register/
{
  "name": "Dr. Sarah Connor",
  "email": "sarah@example.com",
  "password": "SecurePassword123!"
}
```
**Response (201 Created):**
```json
{
  "message": "Registration successful.",
  "user": {
    "id": 1,
    "name": "Dr. Sarah Connor",
    "email": "sarah@example.com"
  }
}
```

#### Example: Login User
```json
POST /api/auth/login/
{
  "email": "sarah@example.com",
  "password": "SecurePassword123!"
}
```
**Response (200 OK):**
```json
{
  "message": "Login successful.",
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "user": {
    "id": 1,
    "name": "Dr. Sarah Connor",
    "email": "sarah@example.com"
  }
}
```

---

### 2. Patient Management APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/patients/` | Add a new patient record | ✅ Yes |
| `GET` | `/api/patients/` | Retrieve all patients created by the authenticated user | ✅ Yes |
| `GET` | `/api/patients/<id>/` | Get details of a specific patient | ✅ Yes |
| `PUT` | `/api/patients/<id>/` | Update all patient details | ✅ Yes |
| `PATCH`| `/api/patients/<id>/` | Partial update of patient details | ✅ Yes |
| `DELETE`| `/api/patients/<id>/` | Delete a patient record | ✅ Yes |

#### Example: Create Patient
```json
POST /api/patients/
{
  "name": "Ananya Rao",
  "age": 28,
  "gender": "Female",
  "phone": "+919876543210",
  "address": "14 Residency Road, Bengaluru, Karnataka"
}
```

---

### 3. Doctor Management APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/doctors/` | Add a new doctor record | ✅ Yes |
| `GET` | `/api/doctors/` | Retrieve all doctors | ✅ Yes |
| `GET` | `/api/doctors/<id>/` | Get details of a specific doctor | ✅ Yes |
| `PUT` | `/api/doctors/<id>/` | Update doctor details | ✅ Yes |
| `PATCH`| `/api/doctors/<id>/` | Partial update of doctor details | ✅ Yes |
| `DELETE`| `/api/doctors/<id>/` | Delete a doctor record | ✅ Yes |

#### Example: Create Doctor
```json
POST /api/doctors/
{
  "name": "Dr. Meera Sharma",
  "specialization": "Cardiology",
  "email": "meera.sharma@hospital.org",
  "phone": "+919811223344"
}
```

---

### 4. Patient-Doctor Mapping APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/mappings/` | Assign a doctor to a patient (`patient`, `doctor`) | ✅ Yes |
| `GET` | `/api/mappings/` | Retrieve all patient-doctor mappings | ✅ Yes |
| `GET` | `/api/mappings/<patient_id>/` | Get all doctors assigned to a specific patient | ✅ Yes |
| `DELETE`| `/api/mappings/<id>/` | Remove a doctor from a patient (by mapping ID or patient ID) | ✅ Yes |

#### Example: Assign Doctor to Patient
```json
POST /api/mappings/
{
  "patient": 1,
  "doctor": 1
}
```

#### Example: Get Doctors Assigned to Specific Patient
```http
GET /api/mappings/1/
```
**Response (200 OK):**
```json
[
  {
    "id": 1,
    "patient": 1,
    "patient_name": "Ananya Rao",
    "doctor": 1,
    "doctor_details": {
      "id": 1,
      "name": "Dr. Meera Sharma",
      "specialization": "Cardiology",
      "email": "meera.sharma@hospital.org",
      "phone": "+919811223344",
      "created_at": "2026-10-11T07:45:00Z",
      "updated_at": "2026-10-11T07:45:00Z"
    },
    "assigned_at": "2026-10-11T07:46:00Z"
  }
]
```

#### Example: Remove Doctor from Patient
```http
DELETE /api/mappings/1/
```
**Response:** `204 No Content`

---

## 📮 Postman Collection

The file [postman/CareBridge.postman_collection.json](file:///d:/downloads/carebridge-healthcare-api/postman/CareBridge.postman_collection.json) is pre-configured with:
1. All 16 assignment endpoints grouped logically into folders.
2. Auto-saving test scripts that store `access_token`, `refresh_token`, `patient_id`, `doctor_id`, and `mapping_id` automatically.
3. Collection variables for `base_url` (`http://127.0.0.1:8000`).

To run:
1. Open Postman -> Click **Import** -> Select `postman/CareBridge.postman_collection.json`.
2. Run the **Register User** and **Login User** requests.
3. Your `access_token` is saved automatically to the collection variables and used across all subsequent requests.
