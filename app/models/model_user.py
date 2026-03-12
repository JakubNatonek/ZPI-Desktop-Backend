from enum import Enum as PyEnum

from sqlalchemy import Column, Enum, Integer, String
from app.database import Base


class RolaEnum(str, PyEnum):
    WYKLADOWCA = "wykladowca"
    CWICZENIA = "cwiczenia"
    LABORATORIUM = "laboratorium"
    SEMINARIUM = "seminarium"
    STUDENT = "student"
    INNE = "inne"


class DzialEnum(str, PyEnum):
    INFORMATYKA = "informatyka"
    MECHATRONIKA = "mechatronika"
    ENERGETYKA = "energetyka"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    login = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rola = Column(
        Enum(
            RolaEnum,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            name="user_rola",
        ),
        nullable=False,
    )
    dzial = Column(
        Enum(
            DzialEnum,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            name="user_dzial",
        ),
        nullable=False,
    )