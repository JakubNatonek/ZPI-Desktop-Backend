from typing import cast

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
from app.cruds.rapla.crud_rapla_permission import get_permission_by_access
from app.cruds.rapla.crud_rapla_permission_for_define_element import add_permission_to_define_element
from app.cruds.rapla.crud_rapla_language_abbreviations import get_language_abbreviation_by_language


def seed_define_przedmiot(db: Session, rapla_admin_uuid: str) -> None:

   uuid = None
   name = "dynatt:przedmiot"
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
      lang_name = create_language_name(db, cast(int, abbrev.id), "Przedmiot")
      try:
         add_language_name_to_define_element(db, cast(int, define.id), cast(int, lang_name.id))
      except Exception:
         pass

   # Annotations from the XML
   annotations = {
      "nameformat": "{name} {activity} {field_of_study_abbrevation} {field_of_study_year}",
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

   # name (string)
   name_elem = create_optional_element(db, "name", default_value="")
   try:
      add_data_type_to_optional_element(db, cast(int, name_elem.id), cast(int, dt_str.id))
   except Exception:
      pass
   try:
      add_optional_to_define(db, cast(int, name_elem.id), cast(int, define.id))
   except Exception:
      pass

   # activity (category: typy_przedmiotow, single select)
   activity = create_optional_element(db, "activity")
   c_activity_root = create_constraint(db, "root-category", "category[key='typy_przedmiotow']")
   c_activity_multi = create_constraint(db, "multi-select", "false")
   try:
      add_data_type_to_optional_element(db, cast(int, activity.id), cast(int, dt_cat.id))
   except Exception:
      pass
   try:
      add_constraint_to_optional_element(db, cast(int, activity.id), cast(int, c_activity_root.id))
   except Exception:
      pass
   try:
      add_constraint_to_optional_element(db, cast(int, activity.id), cast(int, c_activity_multi.id))
   except Exception:
      pass
   try:
      add_optional_to_define(db, cast(int, activity.id), cast(int, define.id))
   except Exception:
      pass

   # room_properties (string)
   room_properties = create_optional_element(db, "room_properties", default_value="")
   try:
      add_data_type_to_optional_element(db, cast(int, room_properties.id), cast(int, dt_str.id))
   except Exception:
      pass
   try:
      add_optional_to_define(db, cast(int, room_properties.id), cast(int, define.id))
   except Exception:
      pass

   # field_of_study_abbrevation (string)
   field_of_study_abbrevation = create_optional_element(db, "field_of_study_abbrevation", default_value="")
   try:
      add_data_type_to_optional_element(db, cast(int, field_of_study_abbrevation.id), cast(int, dt_str.id))
   except Exception:
      pass
   try:
      add_optional_to_define(db, cast(int, field_of_study_abbrevation.id), cast(int, define.id))
   except Exception:
      pass

   # field_of_study_year (int)
   field_of_study_year = create_optional_element(db, "field_of_study_year")
   try:
      add_data_type_to_optional_element(db, cast(int, field_of_study_year.id), cast(int, dt_int.id))
   except Exception:
      pass
   try:
      add_optional_to_define(db, cast(int, field_of_study_year.id), cast(int, define.id))
   except Exception:
      pass

   # Optional display names
   if abbrev is not None:
      label_map = {
         name_elem: "Name",
         activity: "activity",
         room_properties: "room_properties",
         field_of_study_abbrevation: "field of study abbrevation",
         field_of_study_year: "fielld of study year",
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

   print(f"Seeded define element: dynatt:przedmiot (id={define.id})")
