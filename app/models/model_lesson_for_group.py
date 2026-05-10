from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class LessonForGroup(Base):
	__tablename__ = "lesson_for_group"
	__table_args__ = (
		UniqueConstraint("lesson_id", "group_id", name="uq_lesson_for_group"),
	)

	id = Column(Integer, primary_key=True, index=True, autoincrement=True)
	lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
	group_id = Column(Integer, ForeignKey("group.id", ondelete="CASCADE"), nullable=False, index=True)

	lesson = relationship("Lesson")
	group = relationship("Group")
