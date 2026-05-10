from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS

from app.schemas.rapla.resorces.schema_rapla_resourc_nauczyciel import SchemaRaplaResourcNauczyciel
from app.schemas.rapla.resorces.schema_rapla_resourc_przedmiot import SchemaRaplaResourcPrzedmiot
from app.schemas.rapla.resorces.schema_rapla_resourc_room import SchemaRaplaResourcRoom
from app.schemas.rapla.resorces.schema_rapla_resourc_semester import SchemaRaplaResourcSemester
from app.schemas.rapla.resorces.schema_rapla_resourc_grupa import SchemaRaplaResourcGrupa

@dataclass
class SchemaRaplaResources:

    resources_nauczyciel: list[SchemaRaplaResourcNauczyciel] = field(default_factory=lambda: cast(list[SchemaRaplaResourcNauczyciel], []))
    resources_przedmiot: list[SchemaRaplaResourcPrzedmiot] = field(default_factory=lambda: cast(list[SchemaRaplaResourcPrzedmiot], []))
    resources_semester: list[SchemaRaplaResourcSemester] = field(default_factory=lambda: cast(list[SchemaRaplaResourcSemester], []))
    resources_room: list[SchemaRaplaResourcRoom] = field(default_factory=lambda: cast(list[SchemaRaplaResourcRoom], []))
    resources_grupa: list[SchemaRaplaResourcGrupa] = field(default_factory=lambda: cast(list[SchemaRaplaResourcGrupa], []))
    

    def to_xml(self, parent: ET.Element) -> ET.Element:
        resources_el = ET.SubElement(parent, f"{{{RAPLA_NS}}}resources")
        for nauczyciel in self.resources_nauczyciel:
            nauczyciel.to_xml(resources_el)

        for przedmiot in self.resources_przedmiot:
            przedmiot.to_xml(resources_el)

        for semester in self.resources_semester:
            semester.to_xml(resources_el)

        for room in self.resources_room:
            room.to_xml(resources_el)
        
        for grupa in self.resources_grupa:
            grupa.to_xml(resources_el)

        return resources_el
