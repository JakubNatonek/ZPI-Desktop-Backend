
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    login = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    plain_password = Column(String, nullable=True)
    must_change_password = Column(Boolean, nullable=False, default=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)

    # association-object lists (store rows)
    roles_for_user = relationship(
        "RolesForUser", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )

    departments_for_user = relationship(
        "DepartmentsForUser", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )

    # convenience many-to-many access to Role / Department objects
    roles = relationship(
        "Role", 
        secondary="roles_for_user", 
        backref="users"
    )
    departments = relationship(
        "Department", 
        secondary="departments_for_user", 
        backref="users"
    )

    conversation_memberships = relationship(
        "ConversationMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sent_messages = relationship(
        "Message",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    teacher_profile = relationship(
        "Teacher",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    student_profile = relationship(
        "Student",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )