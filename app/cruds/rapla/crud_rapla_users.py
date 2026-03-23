from datetime import datetime

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_user import RaplaUser as RaplaUserModel
from app.schemas.rapla.schema_rapla_user import RaplaUser
from app.schemas.rapla.schema_rapla_users import RaplaUsers


def _format_rapla_datetime(value: datetime | None) -> str:
	if value is None:
		return ""
	return value.isoformat().replace("+00:00", "Z")


def get_all_rapla_users(db: Session) -> list[RaplaUserModel]:
	return db.query(RaplaUserModel).order_by(RaplaUserModel.created_at.asc()).all()


def get_rapla_users_schema(db: Session) -> RaplaUsers:
	users = get_all_rapla_users(db)
	schema_users = [
		RaplaUser(
			uuid=user.uuid,
			created_at=_format_rapla_datetime(user.created_at),
			last_changed=_format_rapla_datetime(user.last_changed),
			username=user.username or "",
			password=user.password or "",
			name=user.name or "",
			email=user.email or "",
			is_admin=bool(user.isadmin),
			xml_value=user.xml_value,
		)
		for user in users
	]
	return RaplaUsers(users=schema_users)
