from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_user_to_app_user import RaplaUserToAppUser


def get_all_rapla_user_mappings(db: Session) -> list[RaplaUserToAppUser]:
	return db.query(RaplaUserToAppUser).order_by(RaplaUserToAppUser.id.asc()).all()


def get_mapping_by_app_user_id(db: Session, app_user_id: int) -> RaplaUserToAppUser | None:
	return db.query(RaplaUserToAppUser).filter(RaplaUserToAppUser.app_user_id == app_user_id).first()


def get_mapping_by_rapla_user_id(db: Session, rapla_user_id: int) -> RaplaUserToAppUser | None:
	return db.query(RaplaUserToAppUser).filter(RaplaUserToAppUser.rapla_user_id == rapla_user_id).first()


def create_rapla_user_mapping(db: Session, app_user_id: int, rapla_user_id: int) -> RaplaUserToAppUser:
	existing = (
		db.query(RaplaUserToAppUser)
		.filter(RaplaUserToAppUser.app_user_id == app_user_id)
		.filter(RaplaUserToAppUser.rapla_user_id == rapla_user_id)
		.first()
	)
	if existing is not None:
		return existing

	mapping = RaplaUserToAppUser(app_user_id=app_user_id, rapla_user_id=rapla_user_id)
	db.add(mapping)
	db.commit()
	db.refresh(mapping)
	return mapping


def delete_rapla_user_mapping(db: Session, app_user_id: int, rapla_user_id: int) -> bool:
	mapping = (
		db.query(RaplaUserToAppUser)
		.filter(RaplaUserToAppUser.app_user_id == app_user_id)
		.filter(RaplaUserToAppUser.rapla_user_id == rapla_user_id)
		.first()
	)
	if mapping is None:
		return False

	db.delete(mapping)
	db.commit()
	return True