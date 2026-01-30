from datetime import datetime, timezone
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    AwareDatetime,
    field_validator,
)


def _ensure_utc(dt: datetime) -> datetime:
    """Convert naive datetime to UTC-aware datetime."""
    if dt is None:
        return dt
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


# Patient Schemas
class PatientCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    email: EmailStr
    phone_number: str | None = Field(None, max_length=20)


class PatientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., gt=0)
    first_name: str
    last_name: str | None
    email: EmailStr
    phone_number: str | None
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def ensure_timezone(cls, v: datetime) -> datetime:
        """Ensure datetime is timezone-aware."""
        return _ensure_utc(v)


# Doctor Schemas
class DoctorCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    specialization: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class DoctorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., gt=0)
    full_name: str
    specialization: str
    is_active: bool
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def ensure_timezone(cls, v: datetime) -> datetime:
        """Ensure datetime is timezone-aware."""
        return _ensure_utc(v)


# Appointment Schemas
class AppointmentCreate(BaseModel):
    patient_id: int = Field(..., gt=0)
    doctor_id: int = Field(..., gt=0)
    start_datetime: AwareDatetime  # Input MUST be timezone-aware
    duration_minutes: int = Field(..., ge=15, le=180)


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., gt=0)
    patient_id: int
    doctor_id: int
    start_datetime: datetime
    duration_minutes: int
    created_at: datetime
    end_datetime: datetime

    @field_validator("start_datetime", "created_at", "end_datetime", mode="before")
    @classmethod
    def ensure_timezone(cls, v: datetime) -> datetime:
        """Ensure datetime is timezone-aware."""
        return _ensure_utc(v)
