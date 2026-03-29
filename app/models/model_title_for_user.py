from sqlalchemy import Column, Integer, ForeignKey

from app.core.database import Base


class TitleForUser(Base):

    __tablename__ = "title_for_user"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    title_id = Column(Integer, ForeignKey("title.id"), nullable=False)
