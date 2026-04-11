
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    album_number = Column(String(5), unique=True, index=True, nullable=False)
    login = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    public_key = Column(Text, nullable=True)
    password_hash = Column(String, nullable=False)
    must_change_password = Column(Boolean, nullable=False, default=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)

    roles_for_user = relationship(
        "RolesForUser",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    departments_for_user = relationship(
        "DepartmentsForUser",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def role(self):
        if not self.roles_for_user:
            return None
        return self.roles_for_user[0].role

    @property
    def department(self):
        if not self.departments_for_user:
            return None
        return self.departments_for_user[0].department


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