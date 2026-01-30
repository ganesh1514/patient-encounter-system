import pytest
from datetime import datetime, timezone, timedelta

from patient_encounter_system.models.models import Appointment
from patient_encounter_system.services.patient_service import (
    delete_patient,
    PatientDeletionError,
)
from patient_encounter_system.services.doctor_service import (
    delete_doctor,
    deactivate_doctor,
    DoctorDeletionError,
)


def test_delete_patient_without_appointments(db_session, sample_patient):
    """Test deleting patient with no appointments succeeds."""
    result = delete_patient(db_session, sample_patient.id)
    assert result is True


def test_delete_patient_with_appointments(db_session, sample_patient, sample_doctor):
    """Test deleting patient with appointments fails."""
    # Create an appointment
    appointment = Appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=30,
    )
    db_session.add(appointment)
    db_session.commit()

    with pytest.raises(PatientDeletionError, match="existing appointments"):
        delete_patient(db_session, sample_patient.id)


def test_delete_patient_not_found(db_session):
    """Test deleting non-existent patient returns False."""
    result = delete_patient(db_session, 999)
    assert result is False


def test_delete_doctor_without_appointments(db_session, sample_doctor):
    """Test deleting doctor with no appointments succeeds."""
    result = delete_doctor(db_session, sample_doctor.id)
    assert result is True


def test_delete_doctor_with_appointments(db_session, sample_patient, sample_doctor):
    """Test deleting doctor with appointments fails."""
    # Create an appointment
    appointment = Appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        start_datetime=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=30,
    )
    db_session.add(appointment)
    db_session.commit()

    with pytest.raises(DoctorDeletionError, match="existing appointments"):
        delete_doctor(db_session, sample_doctor.id)


def test_delete_doctor_not_found(db_session):
    """Test deleting non-existent doctor returns False."""
    result = delete_doctor(db_session, 999)
    assert result is False


def test_deactivate_doctor(db_session, sample_doctor):
    """Test deactivating doctor works."""
    assert sample_doctor.is_active is True

    doctor = deactivate_doctor(db_session, sample_doctor.id)

    assert doctor is not None
    assert doctor.is_active is False


def test_deactivate_doctor_not_found(db_session):
    """Test deactivating non-existent doctor returns None."""
    result = deactivate_doctor(db_session, 999)
    assert result is None
