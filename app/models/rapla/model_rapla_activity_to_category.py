from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaActivityToCategory(Base):
	__tablename__ = "rapla_activity_to_category"

	id = Column(Integer, primary_key=True, index=True, autoincrement=True)
	activity_id = Column(Integer, ForeignKey("activities.id"), index=True, nullable=False)
	category_id = Column(Integer, ForeignKey("rapla_category.id"), index=True, nullable=False)

	activity = relationship("Activity")
	category = relationship("RaplaCategory")

	__table_args__ = (
		UniqueConstraint("activity_id", "category_id", name="uq_rapla_activity_to_category"),
	)
