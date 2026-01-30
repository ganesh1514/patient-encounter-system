# Patient Encounter System

A production-grade Medical Encounter Management System (MEMS) backend API for managing patients, doctors, and medical appointments.

## Features

- **Patient Management**: Create and retrieve patient records
- **Doctor Management**: Create and retrieve doctors with activation status
- **Appointment Scheduling**: Schedule appointments with conflict detection
- **Timezone-Aware**: All datetime values are timezone-aware (UTC)
- **Validation**: Comprehensive input validation using Pydantic

## Tech Stack

- **Framework**: FastAPI
- **Database**: MySQL with SQLAlchemy ORM
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Testing**: pytest with coverage

## Project Structure

```
patient_encounter_system/
├── src/
│   └── patient_encounter_system/
│       ├── main.py
│       ├── database.py
│       ├── models/
│       ├── schemas/
│       └── services/
├── tests/
├── alembic/
├── .github/workflows/ci.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites

- Python 3.10+
- Poetry (package manager)
- MySQL database

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd patient_encounter_system
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Configure environment variables in `.env`:
   ```
   DB_HOST=your_host
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_NAME=your_database
   DB_PORT=3306
   ```

4. Run database migrations:
   ```bash
   poetry run alembic upgrade head
   ```

5. Start the application:
   ```bash
   poetry run uvicorn patient_encounter_system.main:app --reload
   ```

## API Documentation

Access OpenAPI documentation at: `http://localhost:8000/docs`

## API Endpoints

### Patients

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| POST | `/patients` | Create a patient | 201, 400 |
| GET | `/patients/{id}` | Get patient by ID | 200, 404 |

### Doctors

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| POST | `/doctors` | Create a doctor | 201, 400 |
| GET | `/doctors/{id}` | Get doctor by ID | 200, 404 |

### Appointments

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| POST | `/appointments` | Schedule appointment | 201, 400, 409 |
| GET | `/appointments?date=YYYY-MM-DD&doctor_id={optional}` | List appointments | 200 |

## Domain Rules

1. A doctor must not have overlapping appointments
2. Appointments must be scheduled in the future
3. All datetime values must be timezone-aware
4. Appointment duration must be between 15 and 180 minutes
5. Patients or doctors with existing appointments cannot be deleted
6. Inactive doctors cannot accept new appointments

## Running Tests

```bash
# Run all tests with coverage
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_appointment_services.py
```

## Code Quality

```bash
# Linting
poetry run ruff check src/ tests/

# Formatting
poetry run black src/ tests/

# Security check
poetry run bandit -r src/ -ll
```

## License

This project is for educational purposes.