from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import List, cast


from app.schemas.rapla.rapla_namespaces import ANNOTATION_NS
from app.schemas.rapla.schema_rapla_annotation import RaplaAnnotation


@dataclass
class RaplaAnnotations:
	annotations: List[RaplaAnnotation] = field(default_factory=lambda: cast(list[RaplaAnnotation], []))

	def to_xml(self, parent: ET.Element) -> ET.Element:
		annotations_el = ET.SubElement(parent, f"{{{ANNOTATION_NS}}}annotations")
		for annotation in self.annotations:
			annotation.to_xml(annotations_el)
		return annotations_el
	
