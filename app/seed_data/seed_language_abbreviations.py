
from enum import Enum as PyEnum

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.rapla.model_language_abbreviations import RaplaLanguageAbbreviations


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


def seed_language_abbreviations(db: Session | None = None) -> None:
    own_session = db is None
    if db is None:
        db = SessionLocal()

    try:
        for language in LanguageAbbreviationEnum:
            existing = db.query(RaplaLanguageAbbreviations).filter_by(language=language.value).first()
            if existing:
                continue

            db.add(RaplaLanguageAbbreviations(language=language.value))

        if own_session:
            db.commit()
            print("Language abbreviations seeded.")
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_language_abbreviations()
