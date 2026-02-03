from datetime import date
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.database import get_db, engine, Base
from src.schemas.patient import PatientCreate, PatientRead


from src.schemas.doctor import DoctorCreate, DoctorRead

from src.schemas.appointment import AppointmentCreate, AppointmentRead
from src.services.patient_service import (
    create_patient,
    get_patient_by_id,
)
from src.services.doctor_service import (
    create_doctor,
    get_doctor_by_id,
)
from src.services.appointment_service import (
    create_appointment,
    get_appointments_by_date,
    AppointmentConflictError,
    AppointmentValidationError,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Patient Encounter System",
    description="Medical Encounter Management System API",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors with 400 status."""
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


# Patient Endpoints
@app.post("/patients", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient_endpoint(payload: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient record."""
    return create_patient(db, payload)


@app.get("/patients/{patient_id}", response_model=PatientRead)
def get_patient_endpoint(patient_id: int, db: Session = Depends(get_db)):
    """Retrieve a patient by ID."""
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


# Doctor Endpoints
@app.post("/doctors", response_model=DoctorRead, status_code=status.HTTP_201_CREATED)
def create_doctor_endpoint(payload: DoctorCreate, db: Session = Depends(get_db)):
    """Create a new doctor record."""
    return create_doctor(db, payload)


@app.get("/doctors/{doctor_id}", response_model=DoctorRead)
def get_doctor_endpoint(doctor_id: int, db: Session = Depends(get_db)):
    """Retrieve a doctor by ID."""
    doctor = get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


# Appointment Endpoints
@app.post(
    "/appointments", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED
)
def create_appointment_endpoint(
    payload: AppointmentCreate, db: Session = Depends(get_db)
):
    """Schedule a new appointment."""
    try:
        return create_appointment(db, payload)
    except AppointmentConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except AppointmentValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/appointments", response_model=list[AppointmentRead])
def list_appointments_endpoint(
    date: date,
    doctor_id: int | None = None,
    db: Session = Depends(get_db),
):
    """
    List appointments for a specific date.
    Optionally filter by doctor_id.
    """
    return get_appointments_by_date(db, date, doctor_id)
