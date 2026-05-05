from sqlalchemy import Column, Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship

from app.core.database import Base


class Lesson(Base):
	__tablename__ = "lessons"

	id = Column(Integer, primary_key=True, index=True, autoincrement=True)

	date = Column(Date, nullable=False, index=True)
	start_time = Column(Time, nullable=False)
	end_time = Column(Time, nullable=False)
	# duration_minutes = Column(Integer, nullable=True)

	subject_id = Column(Integer, ForeignKey("subject.id"), nullable=False, index=True)
	room_id = Column(Integer, ForeignKey("room.id"), nullable=False, index=True)
	user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, index=True)

	# lesson_type = Column(String(20), nullable=True)
	# groups = Column(String(120), nullable=True)
	# notes = Column(String(240), nullable=True)

	subject = relationship("Subject")
	room = relationship("Room")
	user = relationship("User")
