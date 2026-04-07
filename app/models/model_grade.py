from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class GradeRecord(Base):
    __tablename__ = "grade_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    student_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    lecturer_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    semester = Column(Integer, nullable=False, index=True) # NOTE: This should be propably a seprate table?

    subject_name = Column(String, nullable=False, index=True) # NOTE: This should be propably a seprate table?

    component_label = Column(String, nullable=True) # NOTE: What is this?
    component_info = Column(String, nullable=True) # NOTE: What is this?
    
    grade_value = Column(Float, nullable=False)
    is_final = Column(Boolean, nullable=False, default=False)

    sort_order = Column(Integer, nullable=False, default=0) # <- NOTE: Why this??

    student = relationship("User", foreign_keys=[student_id])
    lecturer = relationship("User", foreign_keys=[lecturer_id])
