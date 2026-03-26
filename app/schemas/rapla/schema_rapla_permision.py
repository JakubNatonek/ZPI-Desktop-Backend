from dataclasses import dataclass
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import RAPLA_NS


@dataclass
class RaplaPermission:
	access: str

	def to_xml(self, parent: ET.Element) -> ET.Element:
		permission = ET.SubElement(
			parent,
			f"{{{RAPLA_NS}}}permission",
			{"access": self.access},
		)

		return permission