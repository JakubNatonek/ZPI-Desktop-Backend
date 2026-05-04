from typing import cast, List

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_category import RaplaCategory
from app.models.rapla.model_rapla_group_for_user import RaplaGroupForUser
from app.schemas.rapla.schema_rapla_group_for_user import RaplaGroupForUser as RaplaGroupForUserSchema


def get_rapla_group_links_by_user_id(db: Session, rapla_user_id: int) -> list[RaplaGroupForUser]:
	return (
		db.query(RaplaGroupForUser)
		.filter(RaplaGroupForUser.rapla_user_id == rapla_user_id)
		.order_by(RaplaGroupForUser.id.asc())
		.all()
	)


def get_rapla_group_keys_by_user_id(db: Session, rapla_user_id: int) -> list[str]:
	group_links = get_rapla_group_links_by_user_id(db, rapla_user_id)
	if not group_links:
		return []

	category_ids = [cast(int, group_link.category_id) for group_link in group_links]
	category_rows = db.query(RaplaCategory).filter(RaplaCategory.id.in_(category_ids)).all()
	category_by_id: dict[int, RaplaCategory] = {
		cast(int, category.id): category for category in category_rows
	}

	return [
		cast(str, category_by_id[cast(int, group_link.category_id)].key)
		for group_link in group_links
		if cast(int, group_link.category_id) in category_by_id
	]


def add_rapla_group_for_user(db: Session, rapla_user_id: int, category_id: int) -> RaplaGroupForUser:
	existing = (
		db.query(RaplaGroupForUser)
		.filter(RaplaGroupForUser.rapla_user_id == rapla_user_id)
		.filter(RaplaGroupForUser.category_id == category_id)
		.first()
	)
	if existing is not None:
		return existing

	group_link = RaplaGroupForUser(rapla_user_id=rapla_user_id, category_id=category_id)
	db.add(group_link)
	db.commit()
	db.refresh(group_link)
	return group_link


def delete_rapla_group_for_user(db: Session, rapla_user_id: int, category_id: int) -> bool:
	group_link = (
		db.query(RaplaGroupForUser)
		.filter(RaplaGroupForUser.rapla_user_id == rapla_user_id)
		.filter(RaplaGroupForUser.category_id == category_id)
		.first()
	)
	if group_link is None:
		return False

	db.delete(group_link)
	db.commit()
	return True


def delete_rapla_group_for_user_by_id(db: Session, rel_id: int) -> bool:
	group_link = (
		db.query(RaplaGroupForUser)
		.filter(RaplaGroupForUser.id == rel_id)
		.first()
	)
	if group_link is None:
		return False

	db.delete(group_link)
	db.commit()
	return True


def get_rapla_user_groups_schema(db: Session, rapla_user_id: int) -> List[RaplaGroupForUserSchema]:
	keys = get_rapla_group_keys_by_user_id(db, rapla_user_id)
	if not keys:
		return []
	return [RaplaGroupForUserSchema(key=f"category[key='{k}']") for k in keys]