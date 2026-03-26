from dataclasses import dataclass
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import RAPLA_NS


@dataclass
class RaplaPermission:
	group: str | None
	access: str

	def to_xml(self, parent: ET.Element) -> ET.Element:
		attributes = {"access": self.access}
		if self.group is not None:
			attributes["group"] = self.group

		permission = ET.SubElement(
			parent,
			f"{{{RAPLA_NS}}}permission",
			attributes,
		)

		return permission