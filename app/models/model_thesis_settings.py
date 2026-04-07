from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ThesisScheduleSettings(Base):
    __tablename__ = "thesis_schedule_settings"

    id = Column(Integer, primary_key=True, default=1)
    tab_visible_from = Column(DateTime(timezone=True), nullable=True)
    tab_visible_to = Column(DateTime(timezone=True), nullable=True)
    topic_submission_from = Column(DateTime(timezone=True), nullable=True)
    topic_submission_to = Column(DateTime(timezone=True), nullable=True)
    proposal_selection_from = Column(DateTime(timezone=True), nullable=True)
    proposal_selection_deadline = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)