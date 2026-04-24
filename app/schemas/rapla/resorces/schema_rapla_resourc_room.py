from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import Iterable, Tuple, cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS, DYNATT_NS
from app.schemas.rapla.schema_rapla_permision import RaplaPermission


@dataclass
class SchemaRaplaResourcRoom:
	uuid: str
	owner: str
	created_at: str
	last_changed: str
	last_changed_by: str

	room_number: str
	seats: int | None = None
	room_type: str | None = None
	departments: list[str] = field(default_factory=lambda: cast(list[str], []))

	permissions: list[RaplaPermission] = field(default_factory=lambda: cast(list[RaplaPermission], []))

	def to_xml(self, parent: ET.Element) -> ET.Element:
		resource = ET.SubElement(
			parent,
			f"{{{RAPLA_NS}}}resource",
		)
		self._add_common_metadata(resource)
		self._add_permissions(resource)

		room = ET.SubElement(
			resource,
			f"{{{DYNATT_NS}}}room",
		)

		room_number_el = ET.SubElement(room, f"{{{DYNATT_NS}}}room_number")
		room_number_el.text = self.room_number

		if self.seats is not None:
			seats_el = ET.SubElement(room, f"{{{DYNATT_NS}}}seats")
			seats_el.text = str(self.seats)

		if self.room_type:
			room_type_el = ET.SubElement(room, f"{{{DYNATT_NS}}}room_type")
			room_type_el.text = f"category[key='{self.room_type}']"

		for department in self.departments:
			if not department:
				continue
			departments_el = ET.SubElement(room, f"{{{DYNATT_NS}}}departments")
			departments_el.text = f"category[key='{department}']"

		return resource

	def _add_permissions(self, parent: ET.Element) -> None:
		for permission in self.permissions:
			permission.to_xml(parent)

	def _add_common_metadata(self, el: ET.Element) -> None:
		for tag, value in self._common_metadata_items():
			el.set(tag, value)

	def _common_metadata_items(self) -> Iterable[Tuple[str, str]]:
		return (
			("id", self.uuid),
			("owner", self.owner),
			("created-at", self.created_at),
			("last-changed", self.last_changed),
			("last-changed-by", self.last_changed_by),
		)
