from dataclasses import dataclass
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import NSMAP, RAPLA_NS


@dataclass
class RaplaUser:
    uuid: str
    created_at: str
    last_changed: str
    username: str = ""
    password: str = ""
    name: str = ""
    email: str = ""
    is_admin: bool = False
    xml_value: str | None = None

    def to_xml(self, parent: ET.Element) -> ET.Element:
        user_el = ET.SubElement(
            parent,
            f"{{{RAPLA_NS}}}user",
            {
                "id": self.uuid,
                "created-at": self.created_at,
                "last-changed": self.last_changed,
                "username": self.username,
                "password": self.password,
                "name": self.name,
                "email": self.email,
                "isAdmin": "true" if self.is_admin else "false",
            },
        )

        if self.xml_value:
            namespace_attrs = " ".join([f'xmlns:{prefix}="{uri}"' for prefix, uri in NSMAP.items()])
            wrapped_xml = f"<wrapper {namespace_attrs}>{self.xml_value}</wrapper>"
            wrapper_el = ET.fromstring(wrapped_xml)
            for child in wrapper_el:
                user_el.append(child)

        return user_el
