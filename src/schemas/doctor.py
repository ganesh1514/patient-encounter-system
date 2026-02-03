from datetime import datetime, timezone
from pydantic import (
    BaseModel,
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
