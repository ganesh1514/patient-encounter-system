from src.services.doctor_service import (
    create_doctor,
    get_doctor_by_id,
)
from src.schemas.doctor import DoctorCreate


def test_create_doctor_success(db_session):
    """Test successful doctor creation."""
    payload = DoctorCreate(
        full_name="Dr. Bob",
        specialization="Orthopedics",
        is_active=True,
    )
    doctor = create_doctor(db_session, payload)

    assert doctor.id is not None
    assert doctor.full_name == "Dr. Bob"
    assert doctor.is_active is True


def test_create_doctor_inactive(db_session):
    """Test creating inactive doctor."""
    payload = DoctorCreate(
        full_name="Dr. Inactive",
        specialization="Dermatology",
        is_active=False,
    )
    doctor = create_doctor(db_session, payload)
    assert doctor.is_active is False


def test_get_doctor_by_id_success(db_session, sample_doctor):
    """Test retrieving doctor by ID."""
    doctor = get_doctor_by_id(db_session, sample_doctor.id)
    assert doctor is not None
    assert doctor.id == sample_doctor.id


def test_get_doctor_by_id_not_found(db_session):
    """Test retrieving non-existent doctor."""
    doctor = get_doctor_by_id(db_session, 999)
    assert doctor is None
