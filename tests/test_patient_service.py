from src.services.patient_service import (
    create_patient,
    get_patient_by_id,
)
from src.schemas.patient import PatientCreate


def test_create_patient_success(db_session):
    """Test successful patient creation."""
    payload = PatientCreate(
        first_name="Alice",
        last_name="Johnson",
        email="alice@example.com",
        phone_number="9876543210",
    )
    patient = create_patient(db_session, payload)

    assert patient.id is not None
    assert patient.first_name == "Alice"
    assert patient.email == "alice@example.com"
    assert patient.created_at is not None


def test_get_patient_by_id_success(db_session, sample_patient):
    """Test retrieving patient by ID."""
    patient = get_patient_by_id(db_session, sample_patient.id)
    assert patient is not None
    assert patient.id == sample_patient.id


def test_get_patient_by_id_not_found(db_session):
    """Test retrieving non-existent patient."""
    patient = get_patient_by_id(db_session, 999)
    assert patient is None
