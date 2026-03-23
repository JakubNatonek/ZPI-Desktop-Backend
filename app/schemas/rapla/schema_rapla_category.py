from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS
from app.schemas.rapla.schema_rapla_language_name import RaplaLanguageName


@dataclass
class RaplaCategory:
    uuid: str
    created_at: str
    last_changed: str
    key: str
    names: list[RaplaLanguageName] = field(default_factory=lambda: cast(list[RaplaLanguageName], []))
    categories: list["RaplaCategory"] | None = None

    def to_xml(self, parent: ET.Element) -> ET.Element:
        category_el = ET.SubElement(
            parent,
            f"{{{RAPLA_NS}}}category",
            {
                "created-at": self.created_at,
                "last-changed": self.last_changed,
                "id": self.uuid,
                "key": self.key,
            },
        )

        for name in self.names:
            name.to_xml(category_el)

        for category in self.categories or []:
            category.to_xml(category_el)

        return category_el