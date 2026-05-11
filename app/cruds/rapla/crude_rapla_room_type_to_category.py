from typing import Optional

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_category import RaplaCategory
from app.models.rapla.model_rapla_room_type_to_category import RaplaRoomTypeToCategory


def get_room_type_category_mapping_by_id(db: Session, mapping_id: int) -> Optional[RaplaRoomTypeToCategory]:
	return (
		db.query(RaplaRoomTypeToCategory)
		.filter(RaplaRoomTypeToCategory.id == mapping_id)
		.first()
	)


def get_room_type_category_mapping(
	db: Session,
	room_type_id: int,
	category_id: int,
) -> Optional[RaplaRoomTypeToCategory]:
	return (
		db.query(RaplaRoomTypeToCategory)
		.filter(
			RaplaRoomTypeToCategory.room_type_id == room_type_id,
			RaplaRoomTypeToCategory.category_id == category_id,
		)
		.first()
	)


def get_categories_for_room_type_id(
	db: Session,
	room_type_id: int,
) -> list[RaplaCategory]:
	return (
		db.query(RaplaCategory)
		.join(RaplaRoomTypeToCategory, RaplaCategory.id == RaplaRoomTypeToCategory.category_id)
		.filter(RaplaRoomTypeToCategory.room_type_id == room_type_id)
		.order_by(RaplaRoomTypeToCategory.id.asc())
		.all()
	)


def create_room_type_category_mapping(
	db: Session,
	room_type_id: int,
	category_id: int,
) -> RaplaRoomTypeToCategory:
	existing = get_room_type_category_mapping(db, room_type_id, category_id)
	if existing is not None:
		return existing

	mapping = RaplaRoomTypeToCategory(
		room_type_id=room_type_id,
		category_id=category_id,
	)
	db.add(mapping)
	db.commit()
	db.refresh(mapping)
	return mapping


def delete_room_type_category_mapping(db: Session, mapping_id: int) -> bool:
	mapping = get_room_type_category_mapping_by_id(db, mapping_id)
	if mapping is None:
		return False

	db.delete(mapping)
	db.commit()
	return True
