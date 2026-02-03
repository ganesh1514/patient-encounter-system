from datetime import datetime, timezone, timedelta
from sqlalchemy import ForeignKey, Integer, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Appointment(Base):
    __tablename__ = "ganesh_b_appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ganesh_b_patients.id"), nullable=False, index=True
    )
    doctor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ganesh_b_doctors.id"), nullable=False, index=True
    )
    start_datetime: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, index=True
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    @property
    def end_datetime(self) -> datetime:
        """Calculate appointment end time (not stored in database)."""
        return self.start_datetime + timedelta(minutes=self.duration_minutes)
