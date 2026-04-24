from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaRoomToResourc(Base):
    __tablename__ = "rapla_room_to_resourc"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("room.id"), index=True, nullable=False)
    rapla_resourc_id = Column(Integer, ForeignKey("rapla_resourc.id"), index=True, nullable=False)

    room = relationship("Room")
    rapla_resourc = relationship("ModelRaplaResourc")

    __table_args__ = (
        UniqueConstraint("room_id", "rapla_resourc_id", name="uq_rapla_room_to_resourc"),
    )
