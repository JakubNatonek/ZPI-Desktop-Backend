from sqlalchemy import Column, ForeignKey, Integer, Table

from app.core.database import Base


room_departments = Table(
    "room_departments",
    Base.metadata,
    Column("room_id", Integer, ForeignKey("room.id"), primary_key=True),
    Column("department_id", Integer, ForeignKey("departments.id"), primary_key=True),
)