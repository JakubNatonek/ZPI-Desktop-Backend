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
from app.models.model_audit_log import AuditLog, AuditLogView
from app.models.model_teaching_load import TeachingLoadAssignment

# -- Rapla models ---------------------------------------------------------
from app.models.rapla.model_rapla_language_abbreviations import RaplaLanguageAbbreviations
from app.models.rapla.model_rapla_language_name_for_category import RaplaLanguageNameForCategory
from app.models.rapla.model_rapla_category import RaplaCategory
from app.models.rapla.model_rapla_department_for_category import RaplaDepartmentForCategory
from app.models.rapla.model_rapla_group_for_user import RaplaGroupForUser
from app.models.rapla.model_rapla_language_name import RaplaLanguageName
from app.models.rapla.model_rapla_resourc import ModelRaplaResourc
from app.models.rapla.model_rapla_room_to_resourc import RaplaRoomToResourc
from app.models.rapla.model_rapla_room_type_to_category import RaplaRoomTypeToCategory
from app.models.rapla.model_rapla_user_to_app_user import RaplaUserToAppUser
from app.models.rapla.model_rapla_user import RaplaUser
from app.models.rapla.model_rapla_title_to_category import RaplaTitleToCategory
from app.models.rapla.model_rapla_annotation import RaplaAnnotation
from app.models.rapla.model_rapla_annotation_for_define_element import RaplaAnnotationForDefineElement
from app.models.rapla.model_rapla_annotation_for_optional_element import RaplaAnnotationForOptionalElement
from app.models.rapla.model_rapla_app_user_to_resourc import RaplaAppUserToResourc
from app.models.rapla.model_rapla_constraint import RaplaConstraint
from app.models.rapla.model_rapla_constraint_for_optional_element import RaplaConstraintForOptionalElement
from app.models.rapla.model_rapla_data_type import RaplaDataType
from app.models.rapla.model_rapla_data_type_for_optional_element import RaplaDataTypeForOptionalElement
from app.models.rapla.model_rapla_define_element import RaplaDefineElement
from app.models.rapla.model_rapla_laguage_name_for_define_element import RaplaLanguageNameForDefineElement
from app.models.rapla.model_rapla_language_name_for_optional_element import RaplaLanguageNameForOptionalElement
from app.models.rapla.model_rapla_optional_element import RaplaOptionalElement
from app.models.rapla.model_rapla_optional_element_for_define_element import RaplaOptionalElementForDefineElement
from app.models.rapla.model_rapla_permission import RaplaPermission
from app.models.rapla.model_rapla_permission_for_define_element import RaplaPermissionForDefineElement
from app.models.rapla.model_rapla_permission_for_resourc import RaplaPermissionForResourc
from app.models.rapla.model_rapla_semester_to_resourc import RaplaSemesterToResourc

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
    "RaplaCategory",
    "RaplaDepartmentForCategory",
    "RaplaGroupForUser",
    "RaplaLanguageAbbreviations",
    "RaplaLanguageName",
    "RaplaLanguageNameForCategory",
    "ModelRaplaResourc",
    "RaplaRoomToResourc",
    "RaplaRoomTypeToCategory",
    "RaplaUser",
    "RaplaUserToAppUser",
]
