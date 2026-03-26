from dataclasses import dataclass
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import RELAXNG_NS


@dataclass
class RaplaOptional:
	optional_element: str

	def to_xml(self, parent: ET.Element) -> ET.Element:
		permission = ET.SubElement(
			parent,
			f"{{{RELAXNG_NS}}}optional",
		)

		return permission