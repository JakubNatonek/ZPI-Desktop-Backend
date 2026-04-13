from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class TitleForUser(Base):

    __tablename__ = "title_for_user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.user_id"), index=True, nullable=False)
    title_id = Column(Integer, ForeignKey("title.id"), index=True, nullable=False)

    user = relationship("User", back_populates="title_assignments")
