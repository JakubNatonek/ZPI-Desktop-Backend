from dataclasses import dataclass
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import ANNOTATION_NS


@dataclass
class RaplaLanguageName:
	language: str
	name: str

	def to_xml(self, parent: ET.Element) -> ET.Element:
		name_el = ET.SubElement(
			parent,
			f"{{{ANNOTATION_NS}}}name",
			{"lang": self.language},
		)
		name_el.text = self.name
		return name_el