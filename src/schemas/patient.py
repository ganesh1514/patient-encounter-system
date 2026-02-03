from datetime import datetime, timezone
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
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
