from app.core.database import Base

# Import models so SQLAlchemy registers table metadata before create_all.

# -- Chat models -----------------------------------------------------------
from app.models.chat.model_conversation import Conversation, ConversationTypeEnum
from app.models.chat.model_conversation_member import ConversationMember
from app.models.chat.model_message import Message

# -- Core application models ----------------------------------------------
from app.models.model_alembic_version import AlembicVersion
from app.models.model_department_for_user import DepartmentsForUser
from app.models.model_department import Department
from app.models.model_group import Group
from app.models.model_refresh_token import RefreshTokenSession
from app.models.model_role_for_user import RolesForUser
from app.models.model_role import Role
from app.models.model_room_type import RoomType
from app.models.model_room import Room
from app.models.model_student import Student
from app.models.model_subject import Subject
from app.models.model_teacher import Teacher
from app.models.model_user import User

# -- Rapla models ---------------------------------------------------------
from app.models.rapla.model_language_abbreviations import RaplaLanguageAbbreviations
from app.models.rapla.model_language_name_for_category import RaplaLanguageNameForCategory
from app.models.rapla.model_rapla_category import RaplaCategory
from app.models.rapla.model_rapla_department_for_category import RaplaDepartmentForCategory
from app.models.rapla.model_rapla_group_for_user import RaplaGroupForUser
from app.models.rapla.model_rapla_language_name import RaplaLanguageName
from app.models.rapla.model_rapla_user_to_app_user import RaplaUserToAppUser
from app.models.rapla.model_rapla_user import RaplaUser

__all__ = [
    "Base",
    "AlembicVersion",
    "Conversation",
    "ConversationTypeEnum",
    "ConversationMember",
    "DepartmentsForUser",
    "Group",
    "Message",
    "RaplaCategory",
    "RaplaDepartmentForCategory",
    "RaplaGroupForUser",
    "RaplaLanguageAbbreviations",
    "RaplaLanguageName",
    "RaplaLanguageNameForCategory",
    "RaplaUser",
    "RaplaUserToAppUser",
    "RefreshTokenSession",
    "RolesForUser",
    "Room",
    "RoomType",
    "Role",
    "Department",
    "Student",
    "Subject",
    "Teacher",
    "User",
]
