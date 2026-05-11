from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaRoomTypeToCategory(Base):
    __tablename__ = "rapla_room_type_to_category"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_type_id = Column(Integer, ForeignKey("room_type.id"), index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("rapla_category.id"), index=True, nullable=False)

    room_type = relationship("RoomType")
    category = relationship("RaplaCategory")

    __table_args__ = (
        UniqueConstraint("room_type_id", "category_id", name="uq_rapla_room_type_to_category"),
    )
