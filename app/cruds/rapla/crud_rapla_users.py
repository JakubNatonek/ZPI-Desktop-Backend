from typing import cast
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_user import RaplaUser as RaplaUserModel
from app.schemas.rapla.schema_rapla_group_for_user import RaplaGroupForUser as RaplaGroupForUserSchema
from app.schemas.rapla.schema_rapla_user import RaplaUser
from app.schemas.rapla.schema_rapla_users import RaplaUsers
from app.cruds.rapla.crud_rapla_group_for_user import get_rapla_group_keys_by_user_id
from app.cruds.rapla.rapla_format_datetime import format_rapla_datetime


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
				created_at=format_rapla_datetime(cast(datetime | None, user.created_at)),
				last_changed=format_rapla_datetime(cast(datetime | None, user.last_changed)),
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


def create_rapla_user(
	db: Session,
	uuid: str | None = None,
	username: str = "",
	email: str = "",
	password: str = "",
	name: str = "",
	isadmin: bool = False,
	created_at: datetime | None = None,
	last_changed: datetime | None = None,
	xml_value: str | None = None,
) -> RaplaUserModel:
		existing_by_username = (
			db.query(RaplaUserModel)
			.filter(RaplaUserModel.username == username)
			.first()
		)
		if existing_by_username:
			raise ValueError(f"Rapla user with username already exists: {username}")

		existing_by_email = (
			db.query(RaplaUserModel)
			.filter(RaplaUserModel.email == email)
			.first()
		)
		if existing_by_email:
			raise ValueError(f"Rapla user with email already exists: {email}")

		now = datetime.now(timezone.utc)
		if created_at is None:
			created_at = now
		
		if last_changed is None:
			last_changed = created_at
		
		if uuid is None:
			uuid = str(uuid4())

		user = RaplaUserModel(
			uuid=uuid,
			created_at=created_at,
			last_changed=last_changed,
			username=username,
			password=password,
			name=name,
			email=email,
			isadmin=isadmin,
			xml_value=xml_value,
		)
		db.add(user)
		db.commit()
		db.refresh(user)
		return user
