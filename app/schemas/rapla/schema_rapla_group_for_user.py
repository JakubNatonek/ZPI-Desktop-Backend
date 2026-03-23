from dataclasses import dataclass
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import RAPLA_NS


@dataclass
class RaplaGroupForUser:
    key: str

    def to_xml(self, parent: ET.Element) -> ET.Element:
        group_el = ET.SubElement(
            parent,
            f"{{{RAPLA_NS}}}group",
            {
                "key": self.key,
            },
        )
        return group_el