from datetime import datetime
from typing import cast

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_user import RaplaUser as RaplaUserModel
from app.schemas.rapla.schema_rapla_group_for_user import RaplaGroupForUser as RaplaGroupForUserSchema
from app.schemas.rapla.schema_rapla_user import RaplaUser
from app.schemas.rapla.schema_rapla_users import RaplaUsers
from app.cruds.rapla.crud_rapla_group_for_user import get_rapla_group_keys_by_user_id


##
# @brief Format a datetime value to Rapla-compatible ISO 8601 string.
# @param value Datetime value or None.
# @return ISO string with Z suffix, or empty string when input is None.
def _format_rapla_datetime(value: datetime | None) -> str:
	if value is None:
		return ""
	return value.isoformat().replace("+00:00", "Z")


##
# @brief Return all Rapla users ordered by creation timestamp.
# @param db Active database session.
# @return List of user model rows.
def get_all_rapla_users(db: Session) -> list[RaplaUserModel]:
	return db.query(RaplaUserModel).order_by(RaplaUserModel.created_at.asc()).all()


##
# @brief Build the Rapla users API schema from database rows.
# @param db Active database session.
# @return Rapla users schema containing all users with mapped fields and groups.
def get_rapla_users_schema(db: Session) -> RaplaUsers:
	users = get_all_rapla_users(db)
	schema_users: list[RaplaUser] = []
	for user in users:
		schema_users.append(
			RaplaUser(
				uuid=cast(str, user.uuid),
				created_at=_format_rapla_datetime(cast(datetime | None, user.created_at)),
				last_changed=_format_rapla_datetime(cast(datetime | None, user.last_changed)),
				username=cast(str | None, user.username) or "",
				password=cast(str | None, user.password) or "",
				name=cast(str | None, user.name) or "",
				email=cast(str | None, user.email) or "",
				is_admin=bool(user.isadmin),
				#groups=get_rapla_user_groups_schema(db, cast(int, user.id)),
				xml_value=cast(str | None, user.xml_value),
			)
		)
	return RaplaUsers(users=schema_users)
