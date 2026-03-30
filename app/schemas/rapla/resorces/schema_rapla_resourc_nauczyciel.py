from dataclasses import dataclass
import xml.etree.ElementTree as ET
from typing import Optional

from app.schemas.rapla.rapla_namespaces import RAPLA_NS, DYNATT_NS
from app.schemas.rapla.schema_interface_rapla_resorc import SchemaInterfaceRaplaResourc


@dataclass
class SchemaRaplaResourcNauczyciel(SchemaInterfaceRaplaResourc):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None

    def to_xml(self, parent: ET.Element) -> ET.Element:
        person = ET.SubElement(
            parent,
            f"{{{RAPLA_NS}}}person",
        )
        # add common metadata defined in the base class
        self._add_common_metadata(person)
        self._add_permissions(person)
        
        nauczyciel = ET.SubElement(
            person,
            f"{{{DYNATT_NS}}}nauczyciel",
        )

        if self.first_name:
            fn = ET.SubElement(nauczyciel, f"{{{DYNATT_NS}}}imie")
            fn.text = self.first_name
        if self.last_name:
            ln = ET.SubElement(nauczyciel, f"{{{DYNATT_NS}}}nazwisko")
            ln.text = self.last_name
        if self.title:
            ln = ET.SubElement(nauczyciel, f"{{{DYNATT_NS}}}tytul")
            ln.text = self.title

        return person