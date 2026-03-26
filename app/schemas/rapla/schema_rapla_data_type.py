from dataclasses import dataclass
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import RELAXNG_NS


@dataclass
class RaplaDataType:
    type: str

    def to_xml(self, parent: ET.Element) -> ET.Element:
        data_type = ET.SubElement(
            parent,
            f"{{{RELAXNG_NS}}}data",
            {"type": self.type},
        )

        return data_type