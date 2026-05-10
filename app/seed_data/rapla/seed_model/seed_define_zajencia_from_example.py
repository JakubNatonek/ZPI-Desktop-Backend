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
from app.cruds.rapla.crud_rapla_permission import (
	create_permission,
	get_permission_by_access,
	get_permission_by_access_and_group,
)
from app.cruds.rapla.crud_rapla_permission_for_define_element import add_permission_to_define_element
from app.cruds.rapla.crud_rapla_language_abbreviations import get_language_abbreviation_by_language


def seed_define_zajencia(db: Session, rapla_admin_uuid: str) -> None:

	uuid = None
	name = "dynatt:zajencia"
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
		lang_name = create_language_name(db, cast(int, abbrev.id), "Zajencia")
		try:
			add_language_name_to_define_element(db, cast(int, define.id), cast(int, lang_name.id))
		except Exception:
			pass

	# Annotations from the XML
	annotations = {
		"nameformat": "{name}",
		"classification-type": "reservation",
		"colors": "rapla:automated",
	}
	for key, value in annotations.items():
		ann = create_annotation(db, key=key, value=value)
		try:
			add_annotation_to_define(db, cast(int, ann.id), cast(int, define.id))
		except Exception:
			pass

	# Optional element: name (rapla:allocatable)
	name_opt = create_optional_element(db, "name")
	dt_alloc = create_data_type(db, "rapla:allocatable")
	try:
		add_data_type_to_optional_element(db, cast(int, name_opt.id), cast(int, dt_alloc.id))
	except Exception:
		pass

	constraints = [
		create_constraint(db, "dynamic-type", "przedmiot"),
		create_constraint(db, "multi-select", "false"),
		create_constraint(db, "belongsTo", "false"),
		create_constraint(db, "package", "false"),
	]
	for constraint in constraints:
		try:
			add_constraint_to_optional_element(db, cast(int, name_opt.id), cast(int, constraint.id))
		except Exception:
			pass

	try:
		add_optional_to_define(db, cast(int, name_opt.id), cast(int, define.id))
	except Exception:
		pass

	# Optional display name
	if abbrev is not None:
		label_name = create_language_name(db, cast(int, abbrev.id), "eventname")
		try:
			add_language_name_to_optional_element(db, cast(int, name_opt.id), cast(int, label_name.id))
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

	p2 = get_permission_by_access_and_group(db, "read", "category[key='read-events-from-others']")
	if p2 is None:
		p2 = create_permission(db, access="read", group="category[key='read-events-from-others']")
	try:
		add_permission_to_define_element(db, cast(int, define.id), cast(int, p2.id))
	except Exception:
		pass

	p3 = get_permission_by_access_and_group(db, "create", "category[key='create-events']")
	if p3 is None:
		p3 = create_permission(db, access="create", group="category[key='create-events']")
	try:
		add_permission_to_define_element(db, cast(int, define.id), cast(int, p3.id))
	except Exception:
		pass

	print(f"Seeded define element: {name} (id={define.id})")
