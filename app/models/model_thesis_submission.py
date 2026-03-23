from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class RequestThesisSubmission(Base):
    __tablename__ = "request_thesis_submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_type_id = Column(Integer, nullable=False, index=True)
    document_type_name = Column(String, nullable=False)
    values = Column(JSON, nullable=False)
    is_approved = Column(Boolean, nullable=False, default=False)
    submitted_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    student_user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True)

    student = relationship("User", foreign_keys=[student_user_id])
    teacher = relationship("User", foreign_keys=[teacher_user_id])
