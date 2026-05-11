from typing import cast

from sqlalchemy.orm import Session

from app.cruds.rapla.crud_rapla_define_element import create_define_element
from app.cruds.rapla.crud_rapla_language_name import create_language_name
from app.cruds.rapla.crud_rapla_language_name_for_define_element import add_language_name_to_define_element
from app.cruds.rapla.crud_rapla_annotation import create_annotation
from app.cruds.rapla.crud_rapla_annotation import get_annotation_by_key
from app.cruds.rapla.crud_rapla_annotation_for_define_element import add_relation as add_annotation_to_define
from app.cruds.rapla.crud_rapla_optional_element import create_optional_element
from app.cruds.rapla.crud_rapla_language_name_for_optional_element import add_language_name_to_optional_element
from app.cruds.rapla.crud_rapla_data_type import create_data_type
from app.cruds.rapla.crud_rapla_data_type_for_optional_element import add_data_type_to_optional_element
from app.cruds.rapla.crud_rapla_constraint import create_constraint
from app.cruds.rapla.crud_rapla_constraint_for_optional_element import add_constraint_to_optional_element
from app.cruds.rapla.crud_rapla_optional_element_for_define_element import add_relation as add_optional_to_define
from app.cruds.rapla.crud_rapla_permission import create_permission
from app.cruds.rapla.crud_rapla_permission import get_permission_by_access
from app.cruds.rapla.crud_rapla_permission_for_define_element import add_permission_to_define_element
from app.cruds.rapla.crud_rapla_language_abbreviations import get_language_abbreviation_by_language

def seed_define_room(db: Session, rapla_admin_uuid: str) -> None:
   """Seed a `dynatt:room` define-element using example data from XML.

   This function does not parse XML; it uses the hard-coded values taken from
   the provided example (doc:name, annotations, optionals and permissions).
   """

   uuid = None
   name = "dynatt:room"
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

   # Define display name
   abbrev = get_language_abbreviation_by_language(db, "en")
   if abbrev is None:
      print("Missing language abbreviation 'en' — skipping name attachment")
   else:
      lang_name = create_language_name(db, cast(int, abbrev.id), "Room")
      try:
         add_language_name_to_define_element(db, cast(int, define.id), cast(int, lang_name.id))
      except Exception:
         pass

   # Annotations from the XML
   annotations = {
      "nameformat": "{room_number} {room_type} {departments}",
      "classification-type": "resource",
      "colors": "rapla:automated",
   }
   for key, value in annotations.items():  
      ann = create_annotation(db, key=key, value=value)
      add_annotation_to_define(db, cast(int, ann.id), cast(int, define.id))


   # Reusable datatypes
   dt_str = create_data_type(db, "string")
   dt_int = create_data_type(db, "int")
   dt_cat = create_data_type(db, "rapla:category")

   # room_number (string)
   room_number = create_optional_element(db, "room_number", default_value="")
   try:
      add_data_type_to_optional_element(db, cast(int, room_number.id), cast(int, dt_str.id))
   except Exception:
      pass
   try:
      add_optional_to_define(db, cast(int, room_number.id), cast(int, define.id))
   except Exception:
      pass

   # seats (integer)
   seats = create_optional_element(db, "seats", default_value="0")
   try:
      add_data_type_to_optional_element(db, cast(int, seats.id), cast(int, dt_int.id))
   except Exception:
      pass
   try:
      add_optional_to_define(db, cast(int, seats.id), cast(int, define.id))
   except Exception:
      pass

   # room_type (category: typy_sal, single select)
   room_type = create_optional_element(db, "room_type")
   c_room_root = create_constraint(db, "root-category", "category[key='typy_sal']")
   c_room_multi = create_constraint(db, "multi-select", "false")
   try:
      add_data_type_to_optional_element(db, cast(int, room_type.id), cast(int, dt_cat.id))
   except Exception:
      pass
   try:
      add_constraint_to_optional_element(db, cast(int, room_type.id), cast(int, c_room_root.id))
   except Exception:
      pass
   try:
      add_constraint_to_optional_element(db, cast(int, room_type.id), cast(int, c_room_multi.id))
   except Exception:
      pass
   try:
      add_optional_to_define(db, cast(int, room_type.id), cast(int, define.id))
   except Exception:
      pass

   # departments (category: kod_budynku, multi-select)
   departments = create_optional_element(db, "departments")
   c_dep_root = create_constraint(db, "root-category", "category[key='kod_budynku']")
   c_dep_multi = create_constraint(db, "multi-select", "false")
   try:
      add_data_type_to_optional_element(db, cast(int, departments.id), cast(int, dt_cat.id))
   except Exception:
      pass
   try:
      add_constraint_to_optional_element(db, cast(int, departments.id), cast(int, c_dep_root.id))
   except Exception:
      pass
   try:
      add_constraint_to_optional_element(db, cast(int, departments.id), cast(int, c_dep_multi.id))
   except Exception:
      pass
   try:
      add_optional_to_define(db, cast(int, departments.id), cast(int, define.id))
   except Exception:
      pass

   # Optional display names
   if abbrev is not None:
      label_map = {
         room_number: "Room number",
         seats: "Seats",
         room_type: "Room type",
         departments: "Departments",
      }
      for optional_element, label in label_map.items():
         label_name = create_language_name(db, cast(int, abbrev.id), label)
         try:
            add_language_name_to_optional_element(
               db,
               cast(int, optional_element.id),
               cast(int, label_name.id),
            )
         except Exception:
            pass

   # Permissions
   p1 = get_permission_by_access(db, "read_type")
   if p1 is None:
      p1 = create_permission(db, access="read_type")
   try:
      add_permission_to_define_element(db, cast(int, define.id), cast(int, p1.id))
   except Exception:
      pass

   p2 = get_permission_by_access(db, "allocate_conflicts")
   if p2 is None:
      p2 = create_permission(db, access="allocate_conflicts")
   try:
      add_permission_to_define_element(db, cast(int, define.id), cast(int, p2.id))
   except Exception:
      pass

   print(f"Seeded define element: dynatt:room (id={define.id})")
