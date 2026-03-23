from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_language_name import RaplaLanguageName


##
# @brief Return all language names ordered by id.
# @param db Active database session.
# @return List of language name rows.
def get_all_language_names(db: Session) -> list[RaplaLanguageName]:
	return db.query(RaplaLanguageName).order_by(RaplaLanguageName.id.asc()).all()


##
# @brief Find a language name by primary key.
# @param db Active database session.
# @param language_name_id Language name identifier.
# @return Matching row or None when not found.
def get_language_name_by_id(db: Session, language_name_id: int) -> RaplaLanguageName | None:
	return db.query(RaplaLanguageName).filter(RaplaLanguageName.id == language_name_id).first()



##
# @brief Create a language name row.
# @param db Active database session.
# @param abbreviation_id Language abbreviation identifier.
# @param name Language display name.
# @return Newly created language name row.
def create_language_name(db: Session, abbreviation_id: int, name: str) -> RaplaLanguageName:
	language_name = RaplaLanguageName(id_abbreviations=abbreviation_id, name=name)
	db.add(language_name)
	db.commit()
	db.refresh(language_name)
	return language_name


##
# @brief Delete a language name by primary key.
# @param db Active database session.
# @param language_name_id Language name identifier.
# @return True if deleted, False when no row was found.
def delete_language_name(db: Session, language_name_id: int) -> bool:
	language_name = get_language_name_by_id(db, language_name_id)
	if language_name is None:
		return False

	db.delete(language_name)
	db.commit()
	return True