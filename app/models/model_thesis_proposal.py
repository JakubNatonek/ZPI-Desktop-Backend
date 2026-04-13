from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.thesis_datetime import utc_now_minute


def _utcnow() -> datetime:
    return utc_now_minute()


class ThesisProposalStatus(str, PyEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ThesisProposal(Base):
    __tablename__ = "thesis_proposals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    student_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    lecturer_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    student_average_grade = Column(Float, nullable=False, default=0.0)
    topic = Column(String(255), nullable=False)
    justification = Column(Text, nullable=False)
    # NOTE: This enum should be a seprate table in db.
    status = Column(
        Enum(
            ThesisProposalStatus,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            name="thesis_proposal_status",
        ),
        nullable=False,
        default=ThesisProposalStatus.PENDING,
    )
    submitted_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    lecturer_topic_id = Column(Integer, ForeignKey("thesis_lecturer_topics.id", ondelete="SET NULL"), nullable=True, index=True)

    student = relationship("User", foreign_keys=[student_id])
    lecturer = relationship("User", foreign_keys=[lecturer_id])
    lecturer_topic = relationship("LecturerTopic", foreign_keys=[lecturer_topic_id])
