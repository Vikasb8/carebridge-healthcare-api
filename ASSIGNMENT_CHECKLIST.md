# Assignment Checklist

- [x] **Django & Django REST Framework**: Structured clean project with settings, URLs, models, serializers, and views.
- [x] **PostgreSQL Database**: Configured via `psycopg` (v3) with environment variables loaded from `.env`.
- [x] **JWT Authentication**: User registration and login implemented with `djangorestframework-simplejwt`, password strength checking, and token refresh.
- [x] **Patient Management APIs**: Full CRUD (`POST`, `GET`, `GET <id>`, `PUT <id>`, `PATCH <id>`, `DELETE <id>`) with row-level ownership isolation.
- [x] **Doctor Management APIs**: Full CRUD (`POST`, `GET`, `GET <id>`, `PUT <id>`, `PATCH <id>`, `DELETE <id>`) secured with authentication.
- [x] **Patient-Doctor Mapping APIs**:
  - `POST /api/mappings/`: Assign doctor to patient with ownership verification.
  - `GET /api/mappings/`: Retrieve all patient-doctor mappings.
  - `GET /api/mappings/<patient_id>/`: Retrieve all doctors assigned to a specific patient with rich doctor details.
  - `DELETE /api/mappings/<id>/`: Remove doctor from patient by mapping ID or patient ID.
- [x] **Django ORM Relationships & Constraints**: Foreign keys, cascades, related names, and `UniqueConstraint(fields=["patient", "doctor"])` preventing duplicate assignments.
- [x] **Error Handling & Validation**: Centralized custom DRF exception handler returning consistent `{"error": ...}` structures, input validation, and HTTP status codes (200, 201, 204, 400, 401, 404).
- [x] **Environment Variables**: Sensitive configuration (`DJANGO_SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) managed via `python-dotenv`.
- [x] **Interactive Documentation**: Swagger UI at `/api/docs/`, ReDoc at `/api/redoc/`, and OpenAPI schema at `/api/schema/`.
- [x] **Automated Test Suite**: 12 comprehensive unit and integration tests passing in `manage.py test`.
- [x] **Postman Collection**: Fully configured collection in `postman/CareBridge.postman_collection.json` with automated token and ID capture scripts.
