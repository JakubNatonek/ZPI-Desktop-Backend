from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaUserToAppUser(Base):
	__tablename__ = "rapla_user_to_app_user"

	id = Column(Integer, primary_key=True, index=True, autoincrement=True)
	app_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
	rapla_user_id = Column(Integer, ForeignKey("rapla_user.id"), nullable=False)

	app_user = relationship("User")
	rapla_user = relationship("RaplaUser")

	__table_args__ = (
		UniqueConstraint("app_user_id", name="uq_rapla_map_app_user_id"),
		UniqueConstraint("rapla_user_id", name="uq_rapla_map_rapla_user_id"),
	)
