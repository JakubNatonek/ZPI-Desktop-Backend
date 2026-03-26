from dataclasses import dataclass
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import RAPLA_NS


@dataclass
class RaplaAnnotation:
    key: str
    value: str

    def to_xml(self, parent: ET.Element) -> ET.Element:
        annotation = ET.SubElement(
            parent,
            f"{{{RAPLA_NS}}}annotation",
            {"key": self.key},
        )
        annotation.text = self.value
        return annotation
	
