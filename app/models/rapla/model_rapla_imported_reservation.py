from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, JSON, String

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RaplaImportedReservation(Base):
    """Stores the last known state of each Rapla reservation imported via file upload.

    Each row corresponds to one <rapla:reservation> element identified by its UUID.
    When a new file is uploaded the values here are compared with the parsed file to
    produce an audit-log diff.
    """

    __tablename__ = "rapla_imported_reservations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Rapla reservation UUID (id attribute on <rapla:reservation>)
    uuid = Column(String(200), nullable=False, unique=True, index=True)

    # <rapla:appointment> fields (only the first appointment is stored)
    start_date = Column(String(20), nullable=True)
    start_time = Column(String(20), nullable=True)
    end_date = Column(String(20), nullable=True)
    end_time = Column(String(20), nullable=True)

    # <rapla:repeating> fields
    repeating_type = Column(String(50), nullable=True)
    repeating_end_date = Column(String(20), nullable=True)

    # Human-readable label from <dynatt:name> inside the reservation
    name = Column(String(500), nullable=True)
    color = Column(String(32), nullable=True)

    # JSON list of idref strings from <rapla:allocate> elements
    allocate = Column(JSON, nullable=True)

    # Reservation type: 'dezyderata' or 'zajencia'
    reservation_type = Column(String(50), nullable=False, server_default="dezyderata")
    # Original rapla:reservation UUID (one reservation may expand to many appointment rows)
    reservation_uuid = Column(String(200), nullable=True, index=True)
    # Activity type resolved from przedmiot resource (e.g. 'wyklady', 'laboratoria')
    activity_type = Column(String(100), nullable=True)

    # Resolved human-readable resource names (populated from XML resource definitions)
    room_names = Column(JSON, nullable=True)       # list[str] — sala(e)
    teacher_names = Column(JSON, nullable=True)    # list[str] — prowadzący
    semester_names = Column(JSON, nullable=True)   # list[str] — semestr(y)
    group_names = Column(JSON, nullable=True)      # list[str] — grupy

    last_imported_at = Column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )
