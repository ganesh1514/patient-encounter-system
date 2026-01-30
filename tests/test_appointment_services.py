import pytest
from datetime import datetime, timedelta
from patient_encounter_system.services.appointment_service import (
    create_appointment,
    get_appointments_by_date,
    AppointmentConflictError,
    AppointmentValidationError,
)
from patient_encounter_system.schemas.schemas import AppointmentCreate


def test_create_appointment_success(
    db_session, sample_patient, sample_doctor, future_datetime
):
    """Test successful appointment creation."""
    payload = AppointmentCreate(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=future_datetime,
        duration_minutes=30,
    )
    appointment = create_appointment(db_session, payload)

    assert appointment.id is not None
    assert appointment.patient_id == sample_patient.id
    assert appointment.doctor_id == sample_doctor.id
    assert appointment.duration_minutes == 30


def test_create_appointment_past_datetime(
    db_session, sample_patient, sample_doctor, past_datetime
):
    """Test appointment in the past is rejected."""
    payload = AppointmentCreate(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=past_datetime,
        duration_minutes=30,
    )

    with pytest.raises(
        AppointmentValidationError, match="must be scheduled in the future"
    ):
        create_appointment(db_session, payload)


# def test_create_appointment_naive_datetime(db_session, sample_patient, sample_doctor):
#     """Test appointment with naive datetime is rejected."""
#     naive_dt = datetime.now() + timedelta(days=1)  # No timezone
#     payload = AppointmentCreate(
#         patient_id=sample_patient.id,
#         doctor_id=sample_doctor.id,
#         start_datetime=naive_dt,
#         duration_minutes=30,
#     )

#     with pytest.raises(AppointmentValidationError, match="timezone-aware"):
#         create_appointment(db_session, payload)


def test_create_appointment_inactive_doctor(
    db_session, sample_patient, inactive_doctor, future_datetime
):
    """Test appointment with inactive doctor is rejected."""
    payload = AppointmentCreate(
        patient_id=sample_patient.id,
        doctor_id=inactive_doctor.id,
        start_datetime=future_datetime,
        duration_minutes=30,
    )

    with pytest.raises(AppointmentValidationError, match="inactive"):
        create_appointment(db_session, payload)


def test_create_appointment_patient_not_found(
    db_session, sample_doctor, future_datetime
):
    """Test appointment with non-existent patient."""
    payload = AppointmentCreate(
        patient_id=999,
        doctor_id=sample_doctor.id,
        start_datetime=future_datetime,
        duration_minutes=30,
    )

    with pytest.raises(AppointmentValidationError, match="Patient not found"):
        create_appointment(db_session, payload)


def test_create_appointment_doctor_not_found(
    db_session, sample_patient, future_datetime
):
    """Test appointment with non-existent doctor."""
    payload = AppointmentCreate(
        patient_id=sample_patient.id,
        doctor_id=999,
        start_datetime=future_datetime,
        duration_minutes=30,
    )

    with pytest.raises(AppointmentValidationError, match="Doctor not found"):
        create_appointment(db_session, payload)


def test_overlapping_appointments_exact_overlap(
    db_session, sample_patient, sample_doctor, future_datetime
):
    """Test exact overlapping appointments are rejected."""
    payload1 = AppointmentCreate(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=future_datetime,
        duration_minutes=60,
    )
    create_appointment(db_session, payload1)

    payload2 = AppointmentCreate(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=future_datetime,
        duration_minutes=30,
    )

    with pytest.raises(AppointmentConflictError, match="overlapping appointment"):
        create_appointment(db_session, payload2)


def test_overlapping_appointments_partial_overlap(
    db_session, sample_patient, sample_doctor, future_datetime
):
    """Test partial overlapping appointments are rejected."""
    payload1 = AppointmentCreate(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=future_datetime,
        duration_minutes=60,
    )
    create_appointment(db_session, payload1)

    payload2 = AppointmentCreate(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=future_datetime + timedelta(minutes=30),
        duration_minutes=60,
    )

    with pytest.raises(AppointmentConflictError, match="overlapping appointment"):
        create_appointment(db_session, payload2)


def test_non_overlapping_appointments(
    db_session, sample_patient, sample_doctor, future_datetime
):
    """Test non-overlapping appointments are allowed."""
    payload1 = AppointmentCreate(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=future_datetime,
        duration_minutes=60,
    )
    create_appointment(db_session, payload1)

    payload2 = AppointmentCreate(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=future_datetime + timedelta(hours=2),
        duration_minutes=30,
    )
    appointment2 = create_appointment(db_session, payload2)

    assert appointment2.id is not None


def test_get_appointments_by_date_empty(db_session):
    """Test getting appointments when none exist."""
    from datetime import date

    result = get_appointments_by_date(db_session, date.today())
    assert result == []


def test_get_appointments_by_date_with_doctor_filter(
    db_session, sample_patient, sample_doctor, future_datetime
):
    """Test getting appointments filtered by doctor."""
    payload = AppointmentCreate(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=future_datetime,
        duration_minutes=30,
    )
    create_appointment(db_session, payload)

    result = get_appointments_by_date(
        db_session, future_datetime.date(), doctor_id=sample_doctor.id
    )
    assert len(result) == 1
    assert result[0].doctor_id == sample_doctor.id


def test_appointment_created_timestamp(
    db_session, sample_patient, sample_doctor, future_datetime
):
    """Test appointment has created_at timestamp."""
    payload = AppointmentCreate(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=future_datetime,
        duration_minutes=30,
    )
    appointment = create_appointment(db_session, payload)

    assert appointment.created_at is not None
