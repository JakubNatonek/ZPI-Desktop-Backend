# from importlib import import_module
# from pathlib import Path
#
# from app.core.database import Base
#
#
# def _import_model_modules() -> None:
#	base_path = Path(__file__).resolve().parent
#	package_prefix = __name__
#
#	for module_path in sorted(base_path.rglob("*.py")):
#		if module_path.name == "__init__.py":
#			continue
#
#		relative_module = module_path.relative_to(base_path).with_suffix("").as_posix().replace("/", ".")
#		module_parts = relative_module.split(".")
#		if any(not part.isidentifier() for part in module_parts):
#			continue
#
#		import_module(f"{package_prefix}.{relative_module}")
#
#
# _import_model_modules()

# NOTE: I understand why, but i still don't like how was done. !!!



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
from app.models.model_grade import GradeRecord
from app.models.model_title import TitleModel
from app.models.model_title_for_user import TitleForUser
from app.models.model_teacher import Teacher
from app.models.model_subject import Subject
from app.models.model_subject_activity import SubjectActivity
from app.models.model_field_of_study import FieldOfStudy
from app.models.model_department_for_field_of_study import DepartmentForFieldOfStudy
from app.models.model_subject_for_field_of_study import SubjectForFieldOfStudy
from app.models.model_announcement import Announcement, AnnouncementSeen
from app.models.model_activity import Activity
from app.models.model_special_equipment import SpecialEquipment
from app.models.model_room_department import room_departments
from app.models.model_refresh_token import RefreshTokenSession
from app.models.model_role_for_user import RolesForUser
from app.models.model_role import Role
from app.models.model_room_type import RoomType
from app.models.model_room import Room
from app.models.model_student import Student
from app.models.model_thesis_proposal import ThesisProposal, ThesisProposalStatus
from app.models.model_thesis_settings import ThesisScheduleSettings
from app.models.model_user import User
from app.models.model_semestr import Semestr
from app.models.model_dezyderata import Dezyderata
from app.models.model_day import Day
from app.models.model_unavailability_note import UnavailabilityNote, NoteType, NoteStatus
from app.models.model_notification import Notification

# -- Rapla models ---------------------------------------------------------
from app.models.rapla.model_rapla_language_abbreviations import RaplaLanguageAbbreviations
from app.models.rapla.model_rapla_activity_to_category import RaplaActivityToCategory
from app.models.rapla.model_rapla_language_name_for_category import RaplaLanguageNameForCategory
from app.models.rapla.model_rapla_category import RaplaCategory
from app.models.rapla.model_rapla_department_for_category import RaplaDepartmentForCategory
from app.models.rapla.model_rapla_group_for_user import RaplaGroupForUser
from app.models.rapla.model_rapla_language_name import RaplaLanguageName
from app.models.rapla.model_rapla_resourc import ModelRaplaResourc
from app.models.rapla.model_rapla_room_to_resourc import RaplaRoomToResourc
from app.models.rapla.model_rapla_subject_to_resourc import RaplaSubjectToResourc
from app.models.rapla.model_rapla_room_type_to_category import RaplaRoomTypeToCategory
from app.models.rapla.model_rapla_user_to_app_user import RaplaUserToAppUser
from app.models.rapla.model_rapla_user import RaplaUser

__all__ = [
    "Base",
    "RefreshTokenSession",
    "RolesForUser",
    "Room",
    "Activity",
    "SpecialEquipment",
    "room_departments",
    "RoomType",
    "Role",
    "Department",
    "Student",
    "Subject",
    "SubjectActivity",
    "FieldOfStudy",
    "DepartmentForFieldOfStudy",
    "SubjectForFieldOfStudy",
    "TitleForUser",
    "TitleModel",
    "Teacher",
    "User",
    "AlembicVersion",
    "Conversation",
    "ConversationTypeEnum",
    "ConversationMember",
    "DepartmentsForUser",
    "Group",
    "Message",
    "UnavailabilityNote",
    "NoteType",
    "NoteStatus",
    "Notification",
    # RAPLA Section
    "RaplaActivityToCategory",
    "RaplaCategory",
    "RaplaDepartmentForCategory",
    "RaplaGroupForUser",
    "RaplaLanguageAbbreviations",
    "RaplaLanguageName",
    "RaplaLanguageNameForCategory",
    "ModelRaplaResourc",
    "RaplaRoomToResourc",
    "RaplaSubjectToResourc",
    "RaplaRoomTypeToCategory",
    "RaplaUser",
    "RaplaUserToAppUser",
]
