from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, Date, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class NoteType(str, Enum):
    """Typ notatki o niedostępności."""
    REQUEST = "request"  # Prośba o wolne
    FORCED = "forced"    # Przymusowa nieobecność (np. chorobowe)


class NoteStatus(str, Enum):
    """Status notatki o niedostępności."""
    PENDING = "pending"           # Oczekująca na rozpatrzenie
    ACCEPTED = "accepted"         # Zaakceptowana
    REJECTED = "rejected"         # Odrzucona
    ACKNOWLEDGED = "acknowledged" # Zapoznano się


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UnavailabilityNote(Base):
    __tablename__ = "unavailability_notes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=True)  # Null dla jednodniowych notek
    description = Column(Text, nullable=True)  # Powód/opis (np. "Choroba", "Urlop")
    note_type = Column(SQLEnum(NoteType), nullable=False, default=NoteType.REQUEST)
    status = Column(SQLEnum(NoteStatus), nullable=False, default=NoteStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    # Relationship
    user = relationship("User", back_populates="unavailability_notes", foreign_keys=[user_id])

    def __repr__(self):
        return f"<UnavailabilityNote(id={self.id}, user_id={self.user_id}, start_date={self.start_date}, status={self.status})>"
