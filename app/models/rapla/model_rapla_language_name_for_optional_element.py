from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaLanguageNameForOptionalElement(Base):
	__tablename__ = "rapla_language_name_for_optional_element"

	# Internal data
	id = Column(Integer, primary_key=True, index=True, autoincrement=True)

	# Rapla data
	optional_element_id = Column(Integer, ForeignKey("rapla_optional_element.id"), index=True, nullable=False)
	language_name_id = Column(Integer, ForeignKey("rapla_language_name.id"), index=True, nullable=False)

	# Relationship
	optional_element = relationship("RaplaOptionalElement")
	language_name = relationship("RaplaLanguageName")

	# Arguments
	__table_args__ = (
		UniqueConstraint("optional_element_id", "language_name_id", name="uq_rapla_language_name_for_optional_element"),
	)
