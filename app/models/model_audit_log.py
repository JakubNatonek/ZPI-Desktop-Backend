from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    entity_name = Column(String(100), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String(20), nullable=False)  # "create" | "update" | "delete"
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    modified_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    modified_by_name = Column(String(200), nullable=False, default="")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=_utcnow, index=True)

    user = relationship("User", foreign_keys=[modified_by])

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, entity={self.entity_name}#{self.entity_id}, action={self.action})>"


class AuditLogView(Base):
    """Tracks the last time each user acknowledged audit log changes."""
    __tablename__ = "audit_log_views"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    last_viewed_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    user = relationship("User", foreign_keys=[user_id])
