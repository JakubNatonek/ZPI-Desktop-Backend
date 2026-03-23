from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS
from app.schemas.rapla.schema_rapla_user import RaplaUser


@dataclass
class RaplaUsers:
    users: list[RaplaUser] = field(default_factory=lambda: cast(list[RaplaUser], []))

    def to_xml(self, parent: ET.Element) -> ET.Element:
        users_el = ET.SubElement(parent, f"{{{RAPLA_NS}}}users")
        users_el.append(ET.Comment(" Users of the system "))
        for user in self.users:
            user.to_xml(users_el)
        return users_el
