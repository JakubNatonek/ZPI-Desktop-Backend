from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.rapla.model_language_abbreviations import RaplaLanguageAbbreviations
from app.models.rapla.model_language_name_for_category import RaplaLanguageNameForCategory
from app.models.rapla.model_rapla_category import RaplaCategory
from app.models.rapla.model_rapla_language_name import RaplaLanguageName


CATEGORY_FIXTURES = [
    {
        "uuid": "ca4f957d-afcc-4c24-a567-52fe0a4621cf",
        "key": "user-groups",
        "parent_uuid": None,
        "name": "user-groups",
    },
    {
        "uuid": "c5b8e52d-e99f-463a-bf4d-57a1f100d34b",
        "key": "read-events-from-others",
        "parent_uuid": "ca4f957d-afcc-4c24-a567-52fe0a4621cf",
        "name": "See events of other users",
    },
    {
        "uuid": "c387e29d-c10f-46eb-a832-aa4e84e2c0f2",
        "key": "create-events",
        "parent_uuid": "ca4f957d-afcc-4c24-a567-52fe0a4621cf",
        "name": "create events",
    },
    {
        "uuid": "c16771b3-6cb2-4f8e-a5a6-9b57e57f8d80",
        "key": "exchange-synchronization",
        "parent_uuid": "ca4f957d-afcc-4c24-a567-52fe0a4621cf",
        "name": "exchange-synchronization",
    },
]


##
# @brief Seed Rapla categories and English names from provided XML fixture.
# @return Number of newly created category-name links.
def seed_language_name_for_category() -> int:
    db: Session = SessionLocal()
    created_links = 0

    try:
        en_abbreviation = (
            db.query(RaplaLanguageAbbreviations)
            .filter(RaplaLanguageAbbreviations.language == "en")
            .first()
        )
        if en_abbreviation is None:
            en_abbreviation = RaplaLanguageAbbreviations(language="en")
            db.add(en_abbreviation)
            db.flush()

        category_by_uuid: dict[str, RaplaCategory] = {}

        # First pass: ensure categories exist (without parent assignment).
        for fixture in CATEGORY_FIXTURES:
            category = (
                db.query(RaplaCategory)
                .filter(RaplaCategory.uuid == fixture["uuid"])
                .first()
            )
            if category is None:
                category = RaplaCategory(
                    uuid=fixture["uuid"],
                    created_at=datetime.now(timezone.utc),
                    last_changed=datetime.now(timezone.utc),
                    key=fixture["key"],
                    parent_id=None,
                )
                db.add(category)
                db.flush()
            else:
                category.key = fixture["key"]

            category_by_uuid[fixture["uuid"]] = category

        # Second pass: assign parent relation.
        for fixture in CATEGORY_FIXTURES:
            parent_uuid = fixture["parent_uuid"]
            category = category_by_uuid[fixture["uuid"]]
            parent = category_by_uuid[parent_uuid] if parent_uuid is not None else None

            target_parent_id = parent.id if parent is not None else None
            if category.parent_id != target_parent_id:
                category.parent_id = target_parent_id

        # Third pass: ensure name + link exist for each category.
        for fixture in CATEGORY_FIXTURES:
            category = category_by_uuid[fixture["uuid"]]

            language_name = (
                db.query(RaplaLanguageName)
                .filter(RaplaLanguageName.id_abbreviations == en_abbreviation.id)
                .filter(RaplaLanguageName.name == fixture["name"])
                .first()
            )
            if language_name is None:
                language_name = RaplaLanguageName(
                    id_abbreviations=en_abbreviation.id,
                    name=fixture["name"],
                )
                db.add(language_name)
                db.flush()

            link = (
                db.query(RaplaLanguageNameForCategory)
                .filter(RaplaLanguageNameForCategory.category_id == category.id)
                .filter(RaplaLanguageNameForCategory.language_name_id == language_name.id)
                .first()
            )
            if link is None:
                db.add(
                    RaplaLanguageNameForCategory(
                        category_id=category.id,
                        language_name_id=language_name.id,
                    )
                )
                created_links += 1

        db.commit()
        return created_links
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    created = seed_language_name_for_category()
    print(f"Seeded category language links: {created}")
