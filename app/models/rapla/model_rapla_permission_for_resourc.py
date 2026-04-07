from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaPermissionForResourc(Base):
	__tablename__ = "rapla_permission_for_rapla_resourc"

	# Internal data
	id = Column(Integer, primary_key=True, index=True, autoincrement=True)

	# Rapla data
	resourc_id = Column(Integer, ForeignKey("rapla_resourc.id"), index=True, nullable=False)
	permission_id = Column(Integer, ForeignKey("rapla_permission.id"), index=True, nullable=False)

	# Relationship
	rapla_resourc = relationship("ModelRaplaResourc")
	permission = relationship("RaplaPermission")

	# Arguments
	__table_args__ = (
		UniqueConstraint("resourc_id", "permission_id", name="uq_rapla_permission_for_rapla_resourc"),
	)
