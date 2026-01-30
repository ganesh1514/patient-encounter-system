import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone, timedelta

from patient_encounter_system.database import Base
from patient_encounter_system.models.models import Patient, Doctor


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_patient(db_session):
    """Create a sample patient."""
    patient = Patient(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


@pytest.fixture
def sample_doctor(db_session):
    """Create a sample active doctor."""
    doctor = Doctor(
        full_name="Dr. Jane Smith",
        specialization="Cardiology",
        is_active=True,
    )
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)
    return doctor


@pytest.fixture
def inactive_doctor(db_session):
    """Create an inactive doctor."""
    doctor = Doctor(
        full_name="Dr. Inactive",
        specialization="Neurology",
        is_active=False,
    )
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)
    return doctor


@pytest.fixture
def future_datetime():
    """Return a future timezone-aware datetime."""
    return datetime.now(timezone.utc) + timedelta(days=1)


@pytest.fixture
def past_datetime():
    """Return a past timezone-aware datetime."""
    return datetime.now(timezone.utc) - timedelta(days=1)
