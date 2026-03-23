from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ThesisProposal(Base):
    __tablename__ = "thesis_proposals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic = Column(String(255), nullable=False)
    justification = Column(Text, nullable=False)

    student_name = Column(String(255), nullable=False)
    student_email = Column(String(255), nullable=False)
    student_average_grade = Column(Float, nullable=False, default=0.0)

    lecturer_user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    student_user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    # Status is stored with booleans to avoid enum persistence.
    is_reviewed = Column(Boolean, nullable=False, default=False)
    is_approved = Column(Boolean, nullable=False, default=False)

    submitted_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    lecturer = relationship("User", foreign_keys=[lecturer_user_id])
    student = relationship("User", foreign_keys=[student_user_id])
