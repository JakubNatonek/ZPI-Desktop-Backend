from dataclasses import dataclass, field
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import RELAXNG_NS
from app.schemas.rapla.schema_rapla_define_element import DefineElement


@dataclass
class Define:
    name: str = "" 
    element: DefineElement = field(default_factory = DefineElement)

    def to_xml(self, parent: ET.Element) -> ET.Element:
        define = ET.SubElement(
            parent,
            f"{{{RELAXNG_NS}}}define",
            {
                "name": self.name,
            },
        )

        self.element.to_xml(define)
        
        return define