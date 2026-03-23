from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS
from app.schemas.rapla.schema_rapla_category import RaplaCategory


@dataclass
class RaplaCategories:
    categories: list[RaplaCategory] = field(default_factory=lambda: cast(list[RaplaCategory], []))

    def to_xml(self, parent: ET.Element) -> ET.Element:
        categories_el = ET.SubElement(parent, f"{{{RAPLA_NS}}}categories")
        for category in self.categories:
            category.to_xml(categories_el)
        return categories_el