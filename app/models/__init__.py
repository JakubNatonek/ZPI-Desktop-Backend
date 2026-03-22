from app.core.database import Base

# Import models so SQLAlchemy registers table metadata before create_all.
from app.models.chat.model_conversation import Conversation, ConversationTypeEnum
from app.models.chat.model_conversation_member import ConversationMember
from app.models.chat.model_message import Message
from app.models.model_alembic_version import AlembicVersion
from app.models.model_group import Group
from app.models.model_teacher import Teacher
from app.models.model_subject import Subject
from app.models.model_refresh_token import RefreshTokenSession
from app.models.model_room import Room
from app.models.model_student import Student
from app.models.model_user import User

__all__ = [
	"Base",
	"AlembicVersion",
	"User",
	"RolaEnum",
	"DzialEnum",
	"RefreshTokenSession",
	"Conversation",
	"ConversationTypeEnum",
	"ConversationMember",
	"Message",
	"Room",
	"Teacher",
	"Student",
	"Group",
	"Subject",
]
