from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaLanguageNameForDefineElement(Base):
	__tablename__ = "rapla_language_name_for_define_element"

	# Internal data
	id = Column(Integer, primary_key=True, index=True, autoincrement=True)

	# Rapla data
	define_element_id = Column(Integer, ForeignKey("rapla_define_element.id"), nullable=False)
	language_name_id = Column(Integer, ForeignKey("rapla_language_name.id"), nullable=False)

	# Relationship
	define_element = relationship("RaplaDefineElement")
	language_name = relationship("RaplaLanguageName")

	# Arguments
	__table_args__ = (
		UniqueConstraint("define_element_id", "language_name_id", name="uq_rapla_language_name_for_define_element"),
	)
