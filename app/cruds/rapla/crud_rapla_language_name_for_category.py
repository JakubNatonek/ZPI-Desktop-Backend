from sqlalchemy.orm import Session

from app.models.rapla.model_language_name_for_category import RaplaLanguageNameForCategory
from app.models.rapla.model_rapla_language_name import RaplaLanguageName


##
# @brief Return all language-name links for a category.
# @param db Active database session.
# @param category_id Category identifier.
# @return List of link rows ordered by id.
def get_language_name_links_by_category_id(db: Session, category_id: int) -> list[RaplaLanguageNameForCategory]:
	return (
		db.query(RaplaLanguageNameForCategory)
		.filter(RaplaLanguageNameForCategory.category_id == category_id)
		.order_by(RaplaLanguageNameForCategory.id.asc())
		.all()
	)


##
# @brief Return language-name rows linked to a category.
# @param db Active database session.
# @param category_id Category identifier.
# @return List of language-name rows ordered by language-name id.
def get_language_name_by_category_id(db: Session, category_id: int) -> list[RaplaLanguageName]:
	return (
		db.query(RaplaLanguageName)
		.join(
			RaplaLanguageNameForCategory,
			RaplaLanguageNameForCategory.language_name_id == RaplaLanguageName.id,
		)
		.filter(RaplaLanguageNameForCategory.category_id == category_id)
		.order_by(RaplaLanguageName.id.asc())
		.all()
	)



##
# @brief Create a link between a category and a language name when missing.
# @param db Active database session.
# @param category_id Category identifier.
# @param language_name_id Language name identifier.
# @return Existing or newly created link row.
def add_language_name_to_category(db: Session, category_id: int, language_name_id: int) -> RaplaLanguageNameForCategory:
	existing = (
		db.query(RaplaLanguageNameForCategory)
		.filter(RaplaLanguageNameForCategory.category_id == category_id)
		.filter(RaplaLanguageNameForCategory.language_name_id == language_name_id)
		.first()
	)
	if existing is not None:
		return existing

	link = RaplaLanguageNameForCategory(category_id=category_id, language_name_id=language_name_id)
	db.add(link)
	db.commit()
	db.refresh(link)
	return link


##
# @brief Delete a link between a category and a language name.
# @param db Active database session.
# @param category_id Category identifier.
# @param language_name_id Language name identifier.
# @return True if deleted, False when no matching link was found.
def delete_language_name_from_category(db: Session, category_id: int, language_name_id: int) -> bool:
	link = (
		db.query(RaplaLanguageNameForCategory)
		.filter(RaplaLanguageNameForCategory.category_id == category_id)
		.filter(RaplaLanguageNameForCategory.language_name_id == language_name_id)
		.first()
	)
	if link is None:
		return False

	db.delete(link)
	db.commit()
	return True


##
# @brief Return all language-name link rows for a category.
# @param db Active database session.
# @param category_id Category identifier.
# @return List of link rows for the provided category.
def _get_language_name_links_for_category(db: Session, category_id: int) -> list[RaplaLanguageNameForCategory]:
	return (
		db.query(RaplaLanguageNameForCategory)
		.filter(RaplaLanguageNameForCategory.category_id == category_id)
		.all()
	)


##
# @brief Delete provided link rows from the category-language-name table.
# @param db Active database session.
# @param links Link rows to delete.
# @return Number of deleted link rows.
def _delete_language_name_links(db: Session, links: list[RaplaLanguageNameForCategory]) -> int:
	for link in links:
		db.delete(link)
	return len(links)


##
# @brief Delete language-name rows that are no longer linked to any category.
# @param db Active database session.
# @param language_name_ids Language-name identifiers to verify.
# @return Number of deleted orphaned language-name rows.
def _delete_orphaned_language_names(db: Session, language_name_ids: set[int]) -> int:
	deleted_language_names = 0
	for language_name_id in language_name_ids:
		has_links = (
			db.query(RaplaLanguageNameForCategory)
			.filter(RaplaLanguageNameForCategory.language_name_id == language_name_id)
			.first()
		)
		if has_links is None:
			language_name = (
				db.query(RaplaLanguageName)
				.filter(RaplaLanguageName.id == language_name_id)
				.first()
			)
			if language_name is not None:
				db.delete(language_name)
				deleted_language_names += 1

	return deleted_language_names


##
# @brief Delete all language-name links for a category and cleanup orphaned language-name rows.
# @param db Active database session.
# @param category_id Category identifier.
# @return Total number of deleted rows across link and language-name tables.
def delete_all_language_names_from_category(db: Session, category_id: int) -> int:
	total_deleted = _delete_all_language_names_from_category(db, category_id)
	db.commit()
	return total_deleted

##
# @brief Delete all language-name links for a category and cleanup orphaned language-name rows.
# @details Performs delete operations in the current transaction and does not commit.
# @param db Active database session.
# @param category_id Category identifier.
# @return Total number of deleted rows across link and language-name tables.
def _delete_all_language_names_from_category(db: Session, category_id: int) -> int:
	links = _get_language_name_links_for_category(db, category_id)

	if not links:
		return 0

	language_name_ids = {link.language_name_id for link in links}
	deleted_links = _delete_language_name_links(db, links)
	deleted_language_names = _delete_orphaned_language_names(db, language_name_ids )

	return deleted_links + deleted_language_names