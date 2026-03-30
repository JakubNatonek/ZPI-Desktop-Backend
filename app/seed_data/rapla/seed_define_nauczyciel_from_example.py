from typing import cast
from datetime import datetime

from sqlalchemy.orm import Session

from app.cruds.rapla.crud_rapla_define_element import create_define_element
from app.cruds.rapla.crud_rapla_language_name import create_language_name
from app.cruds.rapla.crud_rapla_language_name_for_define_element import add_language_name_to_define_element
from app.cruds.rapla.crud_rapla_annotation import create_annotation
from app.cruds.rapla.crud_rapla_annotation_for_define_element import add_relation as add_annotation_to_define
from app.cruds.rapla.crud_rapla_optional_element import create_optional_element
from app.cruds.rapla.crud_rapla_language_name_for_optional_element import add_language_name_to_optional_element
from app.cruds.rapla.crud_rapla_data_type import create_data_type
from app.cruds.rapla.crud_rapla_data_type_for_optional_element import add_data_type_to_optional_element
from app.cruds.rapla.crud_rapla_constraint import create_constraint
from app.cruds.rapla.crud_rapla_constraint_for_optional_element import add_constraint_to_optional_element
from app.cruds.rapla.crud_rapla_optional_element_for_define_element import add_relation as add_optional_to_define
from app.cruds.rapla.crud_rapla_permission import create_permission
from app.cruds.rapla.crud_rapla_permission_for_define_element import add_permission_to_define_element
from app.cruds.rapla.crud_rapla_language_abbreviations import get_language_abbreviation_by_language


def seed_define_nauczyciel(db: Session, rapla_admin_uuid: str) -> None:
    """Seed a `dynatt:nauczyciel` define-element using example data from XML.

    This function does not parse XML; it uses the hard-coded values taken from
    the provided example (doc:name, annotations, optionals and permissions).
    """

    # Example values (from the XML snippet)
    uuid = None
    name = "dynatt:nauczyciel"
    created_at = None
    last_changed = None
    last_changed_by = rapla_admin_uuid

    # Create or get define element
    define = create_define_element(
        db,
        name=name,
        uuid=uuid,
        created_at=created_at,
        last_changed=last_changed,
        last_changed_by=last_changed_by,
    )

    # Add English name: <doc:name lang="en">Nauczyciel</doc:name>
    abbrev = get_language_abbreviation_by_language(db, "en")
    if abbrev is None:
        # language abbreviation missing: nothing to attach
        print("Missing language abbreviation 'en' — skipping name attachment")
    else:
        lang_name = create_language_name(db, cast(int, abbrev.id), "Nauczyciel")
        try:
            add_language_name_to_define_element(db, cast(int, define.id), cast(int, lang_name.id))
        except Exception:
            pass

    # Annotations from the XML
    annotations = {
        "nameformat": "{nazwisko} {imie} {tytul}",
        "classification-type": "person",
        "colors": "rapla:automated",
    }

    for key, value in annotations.items():
        ann = create_annotation(db, key=key, value=value)
        try:
            add_annotation_to_define(db, cast(int, ann.id), cast(int, define.id))
        except Exception:
            pass

    # Optional elements: imie, nazwisko (string); tytul (rapla:category with constraints)
    # imie
    imie = create_optional_element(db, "imie", default_value="")
    dt_str = create_data_type(db, "string")
    try:
        add_data_type_to_optional_element(db, cast(int, imie.id), cast(int, dt_str.id))
    except Exception:
        pass
    try:
        add_optional_to_define(db, cast(int, imie.id), cast(int, define.id))
    except Exception:
        pass

    # nazwisko
    nazwisko = create_optional_element(db, "nazwisko", default_value="")
    try:
        add_data_type_to_optional_element(db, cast(int, nazwisko.id), cast(int, dt_str.id))
    except Exception:
        pass
    try:
        add_optional_to_define(db, cast(int, nazwisko.id), cast(int, define.id))
    except Exception:
        pass

    # tytul: category + constraints
    tytul = create_optional_element(db, "tytul")
    dt_cat = create_data_type(db, "rapla:category")
    try:
        add_data_type_to_optional_element(db, cast(int, tytul.id), cast(int, dt_cat.id))
    except Exception:
        pass

    # constraints (use 'tytul' key per expected XML)
    c_root = create_constraint(db, "root-category", "category[key='tytul']")
    c_multi = create_constraint(db, "multi-select", "false")
    try:
        add_constraint_to_optional_element(db, cast(int, tytul.id), cast(int, c_root.id))
    except Exception:
        pass
    try:
        add_constraint_to_optional_element(db, cast(int, tytul.id), cast(int, c_multi.id))
    except Exception:
        pass

    try:
        add_optional_to_define(db, cast(int, tytul.id), cast(int, define.id))
    except Exception:
        pass

    # Attach language names for optional elements so inner <relax:element> includes doc:name
    abbrev = get_language_abbreviation_by_language(db, "en")
    if abbrev is not None:
        ln_imie = create_language_name(db, cast(int, abbrev.id), "Imie")
        try:
            add_language_name_to_optional_element(db, cast(int, imie.id), cast(int, ln_imie.id))
        except Exception:
            pass

        ln_nazw = create_language_name(db, cast(int, abbrev.id), "Nazwisko")
        try:
            add_language_name_to_optional_element(db, cast(int, nazwisko.id), cast(int, ln_nazw.id))
        except Exception:
            pass

        ln_tyt = create_language_name(db, cast(int, abbrev.id), "Tytuł")
        try:
            add_language_name_to_optional_element(db, cast(int, tytul.id), cast(int, ln_tyt.id))
        except Exception:
            pass

    # Permissions: read_type and allocate_conflicts (no group attribute in XML)
    p1 = create_permission(db, access="read_type")
    try:
        add_permission_to_define_element(db, cast(int, define.id), cast(int, p1.id))
    except Exception:
        pass

    p2 = create_permission(db, access="allocate_conflicts")
    try:
        add_permission_to_define_element(db, cast(int, define.id), cast(int, p2.id))
    except Exception:
        pass

    print(f"Seeded define element: {name} (id={define.id})")
