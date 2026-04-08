from dataclasses import dataclass
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import RAPLA_NS


@dataclass
class SchemaRaplaRepeating:
    type: str
    end_date: str


    def to_xml(self, parent: ET.Element) -> ET.Element:
        repeating = ET.SubElement(
            parent,
            f"{{{RAPLA_NS}}}repeating",
            {
                "type": self.type,
                "end-date": self.end_date,
            },
        )

        return repeating