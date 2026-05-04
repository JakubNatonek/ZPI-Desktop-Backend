from typing import cast

from sqlalchemy.orm import Session

from app.cruds.rapla.crud_rapla_define_element import create_define_element
from app.cruds.rapla.crud_rapla_language_name import create_language_name
from app.cruds.rapla.crud_rapla_language_name_for_define_element import add_language_name_to_define_element
from app.cruds.rapla.crud_rapla_annotation import create_annotation
from app.cruds.rapla.crud_rapla_annotation_for_define_element import add_relation as add_annotation_to_define
from app.cruds.rapla.crud_rapla_annotation_for_optional_element import add_relation as add_annotation_to_optional
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


def seed_define_dezyderata(db: Session, rapla_admin_uuid: str) -> None:
   """Seed a `dynatt:dezyderata` define-element using example data from XML.

   This function does not parse XML; it uses the hard-coded values taken from
   the provided example (doc:name, annotations, optionals and permissions).
   """

   uuid = None
   name = "dynatt:dezyderata"
   created_at = None
   last_changed = None
   last_changed_by = rapla_admin_uuid

   define = create_define_element(
      db,
      name=name,
      uuid=uuid,
      created_at=created_at,
      last_changed=last_changed,
      last_changed_by=last_changed_by,
   )

   # Add English name: <doc:name lang="en">Dezyderata</doc:name>
   abbrev = get_language_abbreviation_by_language(db, "en")
   if abbrev is None:
      print("Missing language abbreviation 'en' — skipping name attachment")
   else:
      lang_name = create_language_name(db, cast(int, abbrev.id), "Dezyderata")
      try:
         add_language_name_to_define_element(db, cast(int, define.id), cast(int, lang_name.id))
      except Exception:
         pass

   # Annotations from the XML
   annotations = {
      "nameformat": "{name}",
      "classification-type": "reservation",
      "colors": "color",
   }

   for key, value in annotations.items():
      ann = create_annotation(db, key=key, value=value)
      try:
         add_annotation_to_define(db, cast(int, ann.id), cast(int, define.id))
      except Exception:
         pass

   # Optional element: name (string, default "Dezyderata")
   name_opt = create_optional_element(db, "name", default_value="Dezyderata")
   dt_str = create_data_type(db, "string")
   try:
      add_data_type_to_optional_element(db, cast(int, name_opt.id), cast(int, dt_str.id))
   except Exception:
      pass
   try:
      add_optional_to_define(db, cast(int, name_opt.id), cast(int, define.id))
   except Exception:
      pass

   # Optional element: color (string, annotations, default "#FF0000")
   color_opt = create_optional_element(db, "color", default_value="#FF0000")
   try:
      add_data_type_to_optional_element(db, cast(int, color_opt.id), cast(int, dt_str.id))
   except Exception:
      pass

   # color optional element annotations
   ann_color = create_annotation(db, key="color", value="true")
   try:
      add_annotation_to_optional(db, cast(int, ann_color.id), cast(int, color_opt.id))
   except Exception:
      pass

   ann_edit = create_annotation(db, key="edit-view", value="no-view")
   try:
      add_annotation_to_optional(db, cast(int, ann_edit.id), cast(int, color_opt.id))
   except Exception:
      pass

   try:
      add_optional_to_define(db, cast(int, color_opt.id), cast(int, define.id))
   except Exception:
      pass

   # Attach language names for optional elements
   if abbrev is not None:
      ln_name = create_language_name(db, cast(int, abbrev.id), "eventname")
      try:
         add_language_name_to_optional_element(db, cast(int, name_opt.id), cast(int, ln_name.id))
      except Exception:
         pass

      ln_color = create_language_name(db, cast(int, abbrev.id), "Color")
      try:
         add_language_name_to_optional_element(db, cast(int, color_opt.id), cast(int, ln_color.id))
      except Exception:
         pass

   # Permissions
   p1 = create_permission(db, access="read_type")
   try:
      add_permission_to_define_element(db, cast(int, define.id), cast(int, p1.id))
   except Exception:
      pass

   p2 = create_permission(db, access="read", group="category[key='read-events-from-others']")
   try:
      add_permission_to_define_element(db, cast(int, define.id), cast(int, p2.id))
   except Exception:
      pass

   #This allows to create for all users
   # p3 = create_permission(db, access="create", group="category[key='create-events']")
   # try:
   #    add_permission_to_define_element(db, cast(int, define.id), cast(int, p3.id))
   # except Exception:
   #    pass

   print(f"Seeded define element: {name} (id={define.id})")
