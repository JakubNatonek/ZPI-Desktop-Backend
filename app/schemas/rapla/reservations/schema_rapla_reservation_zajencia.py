from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import Iterable, Tuple, cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS, DYNATT_NS
from app.schemas.rapla.schema_rapla_permision import RaplaPermission
from app.schemas.rapla.reservations.schema_rapla_apontment import SchemaRaplaApointment


@dataclass
class SchemaRaplaReservationZajencia:
	uuid: str
	owner: str
	created_at: str
	last_changed: str
	last_changed_by: str

	appointments: list[SchemaRaplaApointment]
	name: str

	permissions: list[RaplaPermission] = field(default_factory=lambda: cast(list[RaplaPermission], []))

	def to_xml(self, parent: ET.Element) -> ET.Element:
		reservation = ET.SubElement(
			parent,
			f"{{{RAPLA_NS}}}reservation",
		)
		self._add_common_metadata(reservation)

		zajencia = ET.SubElement(
			reservation,
			f"{{{DYNATT_NS}}}zajencia",
		)
		name_el = ET.SubElement(zajencia, f"{{{DYNATT_NS}}}name")
		name_el.text = self.name

		for appointment in self.appointments:
			appointment.to_xml(reservation)

		self._add_permissions(reservation)
		return reservation

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
