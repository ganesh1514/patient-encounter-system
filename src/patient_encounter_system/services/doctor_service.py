from sqlalchemy.orm import Session
from patient_encounter_system.models.models import Doctor, Appointment
from patient_encounter_system.schemas.schemas import DoctorCreate


class DoctorDeletionError(Exception):
    """Raised when doctor cannot be deleted due to existing appointments."""

    pass


def create_doctor(db: Session, payload: DoctorCreate) -> Doctor:
    """Create a new doctor record."""
    doctor = Doctor(
        full_name=payload.full_name,
        specialization=payload.specialization,
        is_active=payload.is_active,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def get_doctor_by_id(db: Session, doctor_id: int) -> Doctor | None:
    """Retrieve a doctor by ID."""
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()


def deactivate_doctor(db: Session, doctor_id: int) -> Doctor | None:
    """Deactivate a doctor (preferred over deletion)."""
    doctor = get_doctor_by_id(db, doctor_id)
    if not doctor:
        return None

    doctor.is_active = False
    db.commit()
    db.refresh(doctor)
    return doctor


def delete_doctor(db: Session, doctor_id: int) -> bool:
    """
    Delete a doctor if they have no appointments.

    Raises:
        DoctorDeletionError: If doctor has existing appointments

    Returns:
        True if deleted, False if doctor not found
    """
    doctor = get_doctor_by_id(db, doctor_id)
    if not doctor:
        return False

    # Check for existing appointments
    has_appointments = (
        db.query(Appointment).filter(Appointment.doctor_id == doctor_id).first()
    )

    if has_appointments:
        raise DoctorDeletionError("Cannot delete doctor with existing appointments")

    db.delete(doctor)
    db.commit()
    return True
