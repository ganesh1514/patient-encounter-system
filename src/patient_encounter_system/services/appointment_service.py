from datetime import datetime, timezone, timedelta, date, time
from sqlalchemy.orm import Session

from patient_encounter_system.models.models import Appointment, Doctor, Patient
from patient_encounter_system.schemas.schemas import AppointmentCreate


class AppointmentConflictError(Exception):
    """Raised when appointment conflicts with existing appointment."""

    pass


class AppointmentValidationError(Exception):
    """Raised when appointment validation fails."""

    pass


def _ensure_timezone_aware(dt: datetime) -> None:
    """Validate that datetime is timezone-aware."""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise AppointmentValidationError("start_datetime must be timezone-aware")


def _normalize_datetime(dt: datetime) -> datetime:
    """
    Normalize datetime for comparison.
    If naive, assume UTC. If aware, convert to UTC.
    """
    if dt.tzinfo is None:
        # SQLite may return naive datetimes - assume UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _check_overlap(
    existing_start: datetime,
    existing_duration: int,
    new_start: datetime,
    new_duration: int,
) -> bool:
    """
    Check if two appointments overlap.

    Two appointments overlap if:
    - new appointment starts before existing ends AND
    - new appointment ends after existing starts
    """
    # Normalize both datetimes to handle SQLite's naive datetime issue
    existing_start_normalized = _normalize_datetime(existing_start)
    new_start_normalized = _normalize_datetime(new_start)

    existing_end = existing_start_normalized + timedelta(minutes=existing_duration)
    new_end = new_start_normalized + timedelta(minutes=new_duration)

    return new_start_normalized < existing_end and new_end > existing_start_normalized


def create_appointment(db: Session, payload: AppointmentCreate) -> Appointment:
    """
    Create a new appointment with validation and conflict checking.

    Raises:
        AppointmentValidationError: If validation fails
        AppointmentConflictError: If appointment overlaps with existing
    """
    # Validate timezone-aware datetime
    _ensure_timezone_aware(payload.start_datetime)

    # Validate appointment is in the future
    if payload.start_datetime <= datetime.now(timezone.utc):
        raise AppointmentValidationError("Appointment must be scheduled in the future")

    # Validate patient exists
    patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
    if not patient:
        raise AppointmentValidationError("Patient not found")

    # Validate doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id).first()
    if not doctor:
        raise AppointmentValidationError("Doctor not found")

    # Validate doctor is active
    if not doctor.is_active:
        raise AppointmentValidationError("Doctor is inactive")

    # Get all appointments for this doctor
    existing_appointments = (
        db.query(Appointment).filter(Appointment.doctor_id == payload.doctor_id).all()
    )

    # Check for overlaps
    for appt in existing_appointments:
        if _check_overlap(
            appt.start_datetime,
            appt.duration_minutes,
            payload.start_datetime,
            payload.duration_minutes,
        ):
            raise AppointmentConflictError("Doctor has overlapping appointment")

    # Create and persist appointment
    appointment = Appointment(
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        start_datetime=payload.start_datetime,
        duration_minutes=payload.duration_minutes,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointments_by_date(
    db: Session, target_date: date, doctor_id: int | None = None
) -> list[Appointment]:
    """
    Retrieve appointments for a specific date, optionally filtered by doctor.

    Args:
        db: Database session
        target_date: The date to filter appointments
        doctor_id: Optional doctor ID to filter by

    Returns:
        List of appointments for the given date
    """
    # Create datetime range for the target date (UTC)
    start_of_day = datetime.combine(target_date, time.min, tzinfo=timezone.utc)
    end_of_day = datetime.combine(target_date, time.max, tzinfo=timezone.utc)

    query = db.query(Appointment).filter(
        Appointment.start_datetime >= start_of_day,
        Appointment.start_datetime <= end_of_day,
    )

    if doctor_id is not None:
        query = query.filter(Appointment.doctor_id == doctor_id)

    return query.order_by(Appointment.start_datetime).all()
