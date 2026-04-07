from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base

# NOTE: This is usless cose model_title_for_user.py exist. What dose the prop field even do????
class Teacher(Base):
    __tablename__ = "teacher"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    title = Column(String, nullable=True)
    prop = Column(String, nullable=True)

    user = relationship("User", back_populates="teacher_profile")