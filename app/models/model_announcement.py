from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    author = relationship("User", foreign_keys=[author_id])
    seen_by = relationship(
        "AnnouncementSeen",
        back_populates="announcement",
        cascade="all, delete-orphan",
    )


class AnnouncementSeen(Base):
    __tablename__ = "announcement_seen"
    __table_args__ = (
        UniqueConstraint("announcement_id", "user_id", name="uq_announcement_seen_announcement_user"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    announcement_id = Column(Integer, ForeignKey("announcements.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    seen_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    announcement = relationship("Announcement", back_populates="seen_by")
    user = relationship("User", foreign_keys=[user_id])
