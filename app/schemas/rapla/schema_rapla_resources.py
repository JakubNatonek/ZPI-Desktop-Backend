from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS

from app.schemas.rapla.resorces.schema_rapla_resourc_nauczyciel import SchemaRaplaResourcNauczyciel
from app.schemas.rapla.resorces.schema_rapla_resourc_semester import SchemaRaplaResourcSemester


@dataclass
class SchemaRaplaResources:

    resources_nauczyciel: list[SchemaRaplaResourcNauczyciel] = field(default_factory=lambda: cast(list[SchemaRaplaResourcNauczyciel], []))
    resources_semester: list[SchemaRaplaResourcSemester] = field(default_factory=lambda: cast(list[SchemaRaplaResourcSemester], []))
    

    def to_xml(self, parent: ET.Element) -> ET.Element:
        resources_el = ET.SubElement(parent, f"{{{RAPLA_NS}}}resources")
        for nauczyciel in self.resources_nauczyciel:
            nauczyciel.to_xml(resources_el)

        for semester in self.resources_semester:
            semester.to_xml(resources_el)

        return resources_el
