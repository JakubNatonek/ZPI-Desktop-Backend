from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import cast

from app.schemas.rapla.rapla_namespaces import RELAXNG_NS
from app.schemas.rapla.schema_rapla_language_name import RaplaLanguageName

@dataclass
class DefineElement:
    uuid: str
    created_at: str
    last_changed: str
    names: list[RaplaLanguageName] = field(default_factory=lambda: cast(list[RaplaLanguageName], []))
    # annotations TO:DO
    # optional  TO:DO This is definition of a inpur field in Rapla
    # permission TO:DO

    def to_xml(self, parent: ET.Element) -> ET.Element:
        define_element = ET.SubElement(
            parent, 
            f"{{{RELAXNG_NS}}}element",
            {
                "created-at": self.created_at,
                "last-changed": self.last_changed,
                "id": self.uuid,
            },
        )

        for name in self.names:
            name.to_xml(define_element)
    
        return parent