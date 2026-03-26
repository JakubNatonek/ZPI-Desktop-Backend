from dataclasses import dataclass
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import RAPLA_NS


@dataclass
class RaplaConstraint:
    name: str
    value: str

    def to_xml(self, parent: ET.Element) -> ET.Element:
        constraint = ET.SubElement(
            parent,
            f"{{{RAPLA_NS}}}constraint",
            {"name": self.name},
        )
        constraint.text = self.value

        return constraint