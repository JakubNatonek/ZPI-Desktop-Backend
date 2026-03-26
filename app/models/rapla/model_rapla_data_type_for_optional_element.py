from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaDataTypeForOptionalElement(Base):
	__tablename__ = "rapla_data_type_for_optional_element"

	# Internal data
	id = Column(Integer, primary_key=True, index=True, autoincrement=True)

	# Rapla data
	optional_element_id = Column(Integer, ForeignKey("rapla_optional_element.id"), nullable=False)
	data_type_id = Column(Integer, ForeignKey("rapla_data_type.id"), nullable=False)

	# Relationship
	optional_element = relationship("RaplaOptionalElement")
	data_type = relationship("RaplaDataType")

	# Arguments
	__table_args__ = (
		UniqueConstraint("optional_element_id", "data_type_id", name="uq_rapla_data_type_for_optional_element"),
	)
