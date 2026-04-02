from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaAppUserToResourc(Base):
    __tablename__ = "rapla_app_user_to_resourc"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    app_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    rapla_resourc_id = Column(Integer, ForeignKey("rapla_resourc.id"), nullable=False)

    app_user = relationship("User")
    rapla_resourc = relationship("ModelRaplaResourc")

    __table_args__ = (
        UniqueConstraint("app_user_id", "rapla_resourc_id", name="uq_rapla_app_user_to_resourc"),
    )
