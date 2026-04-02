from importlib import import_module
from pathlib import Path

from app.core.database import Base


def _import_model_modules() -> None:
	base_path = Path(__file__).resolve().parent
	package_prefix = __name__

	for module_path in sorted(base_path.rglob("*.py")):
		if module_path.name == "__init__.py":
			continue

		relative_module = module_path.relative_to(base_path).with_suffix("").as_posix().replace("/", ".")
		module_parts = relative_module.split(".")
		if any(not part.isidentifier() for part in module_parts):
			continue

		import_module(f"{package_prefix}.{relative_module}")


_import_model_modules()

# Import models so SQLAlchemy registers table metadata before create_all.
from app.models.chat.model_conversation import Conversation, ConversationTypeEnum
from app.models.chat.model_conversation_member import ConversationMember
from app.models.chat.model_message import Message
from app.models.model_alembic_version import AlembicVersion
from app.models.model_group import Group
from app.models.model_grade import GradeRecord
from app.models.model_teacher import Teacher
from app.models.model_subject import Subject
from app.models.model_announcement import Announcement, AnnouncementSeen
from app.models.model_refresh_token import RefreshTokenSession
from app.models.model_room import Room
from app.models.model_student import Student
from app.models.model_thesis_proposal import ThesisProposal, ThesisProposalStatus
from app.models.model_thesis_settings import ThesisScheduleSettings
from app.models.model_user import User
from app.models.model_semestr import Semestr
from app.models.model_dezyderata import Dezyderata
from app.models.model_day import Day

__all__ = [
	# nie musisz dodawac modeli
	# wszystkie tabelki robi ta funkcja: _import_model_modules()
]
