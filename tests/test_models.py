from datetime import datetime, timezone, timedelta
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.appointment import Appointment


def test_patient_creation(db_session):
    """Test patient model creation."""
    patient = Patient(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        phone_number="1234567890",
    )
    db_session.add(patient)
    db_session.commit()

    assert patient.id is not None
    assert patient.created_at is not None
    assert patient.updated_at is not None


def test_doctor_creation(db_session):
    """Test doctor model creation."""
    doctor = Doctor(
        full_name="Dr. Test",
        specialization="General",
        is_active=True,
    )
    db_session.add(doctor)
    db_session.commit()

    assert doctor.id is not None
    assert doctor.created_at is not None


def test_appointment_end_datetime_property(db_session, sample_patient, sample_doctor):
    """Test appointment end_datetime derived property."""
    start = datetime.now(timezone.utc) + timedelta(days=1)
    duration = 60

    appointment = Appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=start,
        duration_minutes=duration,
    )
    db_session.add(appointment)
    db_session.commit()

    # Verify end_datetime is calculated correctly (compare duration, not exact datetime)
    # SQLite may lose timezone info, so we compare the time difference
    expected_duration = timedelta(minutes=duration)
    actual_duration = appointment.end_datetime - appointment.start_datetime

    assert actual_duration == expected_duration
    assert appointment.duration_minutes == 60


def test_patient_timestamps_auto_set(db_session):
    """Test patient timestamps are automatically set."""
    patient = Patient(
        first_name="Auto",
        last_name="Timestamp",
        email="auto.timestamp@example.com",
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    assert patient.created_at is not None
    assert patient.updated_at is not None


def test_doctor_default_active_status(db_session):
    """Test doctor is active by default."""
    doctor = Doctor(
        full_name="Dr. Default",
        specialization="General",
    )
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)

    assert doctor.is_active is True
