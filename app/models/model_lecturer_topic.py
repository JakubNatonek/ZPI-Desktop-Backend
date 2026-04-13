from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.thesis_datetime import utc_now_minute


def _utcnow() -> datetime:
    return utc_now_minute()


class LecturerTopic(Base):
    __tablename__ = "thesis_lecturer_topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lecturer_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_taken = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    lecturer = relationship("User", foreign_keys=[lecturer_id])
