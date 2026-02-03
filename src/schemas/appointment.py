from datetime import datetime, timezone
from pydantic import (
    BaseModel,
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
