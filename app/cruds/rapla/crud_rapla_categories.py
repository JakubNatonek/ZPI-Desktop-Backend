from datetime import datetime

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_category import RaplaCategory


##
# @brief Return all categories ordered by key.
# @param db Active database session.
# @return List of category rows.
def get_all_rapla_categories(db: Session) -> list[RaplaCategory]:
    return db.query(RaplaCategory).order_by(RaplaCategory.key.asc()).all()


##
# @brief Find a category by primary key.
# @param db Active database session.
# @param category_id Category identifier.
# @return Matching row or None when not found.
def get_rapla_category_by_id(db: Session, category_id: int) -> RaplaCategory | None:
    return db.query(RaplaCategory).filter(RaplaCategory.id == category_id).first()


##
# @brief Find a category by Rapla UUID.
# @param db Active database session.
# @param uuid Category UUID.
# @return Matching row or None when not found.
def get_rapla_category_by_uuid(db: Session, uuid: str) -> RaplaCategory | None:
    return db.query(RaplaCategory).filter(RaplaCategory.uuid == uuid).first()



##
# @brief Find child categories for a given parent category id.
# @param db Active database session.
# @param parent_id Parent category identifier.
# @return List of child categories ordered by key, or None when parent does not exist.
def get_rapla_categories_by_parent_id(db: Session, parent_id: int) -> list[RaplaCategory] | None:
    parent = get_rapla_category_by_id(db, parent_id)
    if parent is None:
        return None

    return (
        db.query(RaplaCategory)
        .filter(RaplaCategory.parent_id == parent_id)
        .order_by(RaplaCategory.key.asc())
        .all()
    )


##
# @brief Find child categories for a given parent category UUID.
# @param db Active database session.
# @param parent_uuid Parent category UUID.
# @return List of child categories ordered by key, or None when parent does not exist.
def get_rapla_categories_by_parent_uuid(db: Session, parent_uuid: str) -> list[RaplaCategory] | None:
    parent = get_rapla_category_by_uuid(db, parent_uuid)
    if parent is None:
        return None

    return (
        db.query(RaplaCategory)
        .filter(RaplaCategory.parent_id == parent.id)
        .order_by(RaplaCategory.key.asc())
        .all()
    )


##
# @brief Create a category if UUID is not already present.
# @param db Active database session.
# @param uuid Rapla UUID.
# @param created_at Creation datetime.
# @param last_changed Last changed datetime.
# @param key Category key.
# @param parent_id Optional parent category id.
# @return Existing or newly created category row.
def create_rapla_category(
    db: Session,
    uuid: str,
    created_at: datetime | None,
    last_changed: datetime | None,
    key: str,
    parent_id: int | None = None,
) -> RaplaCategory:
    existing = get_rapla_category_by_uuid(db, uuid)
    if existing is not None:
        return existing

    category = RaplaCategory(
        uuid=uuid,
        created_at=created_at,
        last_changed=last_changed,
        key=key,
        parent_id=parent_id,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


##
# @brief Delete all child categories recursively for a given parent id.
# @param db Active database session.
# @param parent_id Parent category identifier.
# @return True if parent exists and deletion was processed, False when parent was not found.
def delete_rapla_child_categories_by_parent_id(db: Session, parent_id: int) -> bool:
    parent = get_rapla_category_by_id(db, parent_id)
    if parent is None:
        return False

    children = get_rapla_categories_by_parent_id(db, parent_id)
    if not children:
        return True

    for child in children:
        delete_rapla_child_categories_by_parent_id(db, child.id)
        _delete_rapla_category_by_id(db, child.id)

    return True


##
# @brief Delete all child categories recursively for a given parent UUID.
# @param db Active database session.
# @param parent_uuid Parent category UUID.
# @return True if parent exists and deletion was processed, False when parent was not found.
def delete_rapla_child_categories_by_parent_uuid(db: Session, parent_uuid: str) -> bool:
    parent = get_rapla_category_by_uuid(db, parent_uuid)
    if parent is None:
        return False

    children = get_rapla_categories_by_parent_uuid(db, parent_uuid)
    if not children:
        return True

    for child in children:
        delete_rapla_child_categories_by_parent_uuid(db, child.uuid)
        _delete_rapla_category_by_uuid(db, child.uuid)

    return True


##
# @brief Delete a category by primary key.
# @param db Active database session.
# @param category_id Category identifier.
# @return True if deleted, False when no row was found.
def delete_rapla_category_by_id(db: Session, category_id: int) -> bool:
    category = get_rapla_category_by_id(db, category_id)
    if category is None:
        return False

    delete_rapla_child_categories_by_parent_id(db, category_id)
    db.delete(category)
    db.commit()
    return True

##
# @brief Delete a category by primary key.
# @param db Active database session.
# @param category_id Category identifier.
# @return True if deleted, False when no row was found.
def _delete_rapla_category_by_id(db: Session, category_id: int) -> bool:
    category = get_rapla_category_by_id(db, category_id)
    if category is None:
        return False

    db.delete(category)
    return True

##
# @brief Delete a category by UUID.
# @param db Active database session.
# @param uuid Category UUID.
# @return True if deleted, False when no row was found.
def delete_rapla_category_by_uuid(db: Session, uuid: str) -> bool:
    category = get_rapla_category_by_uuid(db, uuid)
    if category is None:
        return False

    delete_rapla_child_categories_by_parent_uuid(db, uuid)
    db.delete(category)
    db.commit()
    return True

##
# @brief Delete a category by UUID.
# @param db Active database session.
# @param uuid Category UUID.
# @return True if deleted, False when no row was found.
def _delete_rapla_category_by_uuid(db: Session, uuid: str) -> bool:
    category = get_rapla_category_by_uuid(db, uuid)
    if category is None:
        return False
    
    db.delete(category)
    return True

