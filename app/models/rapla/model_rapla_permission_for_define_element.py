from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaPermissionForDefineElement(Base):
	__tablename__ = "rapla_permission_for_define_element"

	# Internal data
	id = Column(Integer, primary_key=True, index=True, autoincrement=True)

	# Rapla data
	define_element_id = Column(Integer, ForeignKey("rapla_define_element.id"), index=True, nullable=False)
	permission_id = Column(Integer, ForeignKey("rapla_permission.id"), index=True, nullable=False)

	# Relationship
	define_element = relationship("RaplaDefineElement")
	permission = relationship("RaplaPermission")

	# Arguments
	__table_args__ = (
		UniqueConstraint("define_element_id", "permission_id", name="uq_rapla_permission_for_define_element"),
	)
