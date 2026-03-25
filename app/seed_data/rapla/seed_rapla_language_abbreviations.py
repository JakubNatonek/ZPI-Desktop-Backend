from enum import Enum as PyEnum

from sqlalchemy.orm import Session

from app.cruds.rapla.crud_rapla_language_abbreviations import create_language_abbreviation


class LanguageAbbreviationEnum(str, PyEnum):
    CS = "cs"
    ES = "es"
    FR = "fr"
    DE = "de"
    EN = "en"
    PT = "pt"
    FI = "fi"
    PL = "pl"
    NL = "nl"


def seed_language_abbreviations(db: Session) -> None:
    for language in LanguageAbbreviationEnum:
        try:
            create_language_abbreviation(db, language.value)
        except ValueError:
            # already exists, ignore
            continue

    print("Language abbreviations seeded.")