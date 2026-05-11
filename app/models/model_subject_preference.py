from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class SubjectPreference(Base):
    __tablename__ = "subject_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject_id = Column(
        Integer,
        ForeignKey("subject.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    __table_args__ = (UniqueConstraint("user_id", "subject_id"),)

    # Relationships
    user = relationship("User", backref="subject_preferences")
    subject = relationship("Subject", backref="user_preferences")
