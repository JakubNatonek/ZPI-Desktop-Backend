from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaLanguageNameForCategory(Base):
	__tablename__ = "rapla_language_name_for_category"

	# Internal data
	id = Column(Integer, primary_key=True, index=True, autoincrement=True)

	# Rapla data
	category_id = Column(Integer, ForeignKey("rapla_category.id"), nullable=False)
	language_name_id = Column(Integer, ForeignKey("rapla_language_name.id"), nullable=False)

	# Relationship
	category = relationship("RaplaCategory")
	language_name = relationship("RaplaLanguageName")

	# Arguments
	__table_args__ = (
		UniqueConstraint("category_id", "language_name_id", name="uq_rapla_language_name_for_category"),
	)
