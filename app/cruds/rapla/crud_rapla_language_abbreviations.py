from sqlalchemy.orm import Session

from app.models.rapla.model_language_abbreviations import RaplaLanguageAbbreviations


##
# @brief Return all language abbreviations sorted by language name.
# @param db Active database session.
# @return List of language abbreviation rows.
def get_all_language_abbreviations(db: Session) -> list[RaplaLanguageAbbreviations]:
	return db.query(RaplaLanguageAbbreviations).order_by(RaplaLanguageAbbreviations.language.asc()).all()


##
# @brief Find a language abbreviation row by primary key.
# @param db Active database session.
# @param abbreviation_id Row identifier.
# @return Matching row or None when not found.
def get_language_abbreviation_by_id(db: Session, abbreviation_id: int) -> RaplaLanguageAbbreviations | None:
	return db.query(RaplaLanguageAbbreviations).filter(RaplaLanguageAbbreviations.id == abbreviation_id).first()


def get_language_abbreviation_by_language(db: Session, language: str) -> RaplaLanguageAbbreviations | None:
	return db.query(RaplaLanguageAbbreviations).filter(RaplaLanguageAbbreviations.language == language).first()


##
# @brief Create a language abbreviation if it does not already exist.
# @param db Active database session.
# @param language Language code/value to create.
# @return Existing or newly created row.
def create_language_abbreviation(db: Session, language: str) -> RaplaLanguageAbbreviations:
	existing = get_language_abbreviation_by_language(db, language)
	if existing is not None:
		raise ValueError(f"Language abbreviation already exists: {language}")

	abbreviation = RaplaLanguageAbbreviations(language=language)
	db.add(abbreviation)
	db.commit()
	db.refresh(abbreviation)
	return abbreviation


##
# @brief Delete a language abbreviation by language value.
# @param db Active database session.
# @param language Language code/value to delete.
# @return True if deleted, False when no row was found.
def delete_language_abbreviation(db: Session, language: str) -> bool:
	abbreviation = get_language_abbreviation_by_language(db, language)
	if abbreviation is None:
		return False

	db.delete(abbreviation)
	db.commit()
	return True


##
# @brief Delete a language abbreviation by primary key.
# @param db Active database session.
# @param abbreviation_id Row identifier to delete.
# @return True if deleted, False when no row was found.
def delete_language_abbreviation_by_id(db: Session, abbreviation_id: int) -> bool:
	abbreviation = get_language_abbreviation_by_id(db, abbreviation_id)
	if abbreviation is None:
		return False

	db.delete(abbreviation)
	db.commit()
	return True