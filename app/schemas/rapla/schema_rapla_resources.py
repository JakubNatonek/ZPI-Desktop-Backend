from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS

from app.schemas.rapla.schema_interface_rapla_resorc import SchemaInterfaceRaplaResourc


@dataclass
class SchemaRaplaResources:

    resources: list[SchemaInterfaceRaplaResourc] = field(default_factory=lambda: cast(list[SchemaInterfaceRaplaResourc], []))

    def to_xml(self, parent: ET.Element) -> ET.Element:


        resources_el = ET.SubElement(parent, f"{{{RAPLA_NS}}}resources")
        for resourc_el in self.resources:
            resourc_el.to_xml(resources_el)

        return resources_el
