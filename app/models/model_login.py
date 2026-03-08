from sqlalchemy import Column, Integer, String
from app.database import Base


# TODO: Replace with actual login model fields (username, password_hash, email, etc.)
class Login(Base):
    __tablename__ = "logins"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)  # TODO: Replace with real fields
