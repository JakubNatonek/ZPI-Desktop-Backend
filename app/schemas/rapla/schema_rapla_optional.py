from dataclasses import dataclass
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import RELAXNG_NS
from app.schemas.rapla.schema_rapla_optional_element import OptionalElement



@dataclass
class RaplaOptional:
	optional_element: OptionalElement

	def to_xml(self, parent: ET.Element) -> ET.Element:
		otional = ET.SubElement(
			parent,
			f"{{{RELAXNG_NS}}}optional",
		)

		self.optional_element.to_xml(otional)

		return otional