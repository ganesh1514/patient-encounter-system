from sqlalchemy.orm import Session
from src.models.patient import Patient
from src.models.appointment import Appointment
from src.schemas.patient import PatientCreate


class PatientDeletionError(Exception):
    """Raised when patient cannot be deleted due to existing appointments."""

    pass


def create_patient(db: Session, payload: PatientCreate) -> Patient:
    """Create a new patient record."""
    patient = Patient(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone_number=payload.phone_number,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient_by_id(db: Session, patient_id: int) -> Patient | None:
    """Retrieve a patient by ID."""
    return db.query(Patient).filter(Patient.id == patient_id).first()


def delete_patient(db: Session, patient_id: int) -> bool:
    """
    Delete a patient if they have no appointments.

    Raises:
        PatientDeletionError: If patient has existing appointments

    Returns:
        True if deleted, False if patient not found
    """
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        return False

    # Check for existing appointments
    has_appointments = (
        db.query(Appointment).filter(Appointment.patient_id == patient_id).first()
    )

    if has_appointments:
        raise PatientDeletionError("Cannot delete patient with existing appointments")

    db.delete(patient)
    db.commit()
    return True
