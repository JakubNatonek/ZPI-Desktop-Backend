from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import cast

from app.schemas.rapla.rapla_namespaces import RELAXNG_NS
from app.schemas.rapla.schema_rapla_language_name import RaplaLanguageName
from app.schemas.rapla.schema_rapla_annotations import RaplaAnnotations
from app.schemas.rapla.schema_rapla_permision import RaplaPermission
from app.schemas.rapla.schema_rapla_optional import RaplaOptional

@dataclass
class DefineElement:
    uuid: str
    created_at: str
    last_changed: str
    last_changed_by: str
    name: str
    names: list[RaplaLanguageName] = field(default_factory=lambda: cast(list[RaplaLanguageName], []))
    annotations: RaplaAnnotations = field(default_factory=lambda: RaplaAnnotations())
    optionals: list[RaplaOptional] = field(default_factory=lambda: cast(list[RaplaOptional], [])) # definition of fields for object (resorce / person)
    permissions: list[RaplaPermission] = field(default_factory=lambda: cast(list[RaplaPermission], []))

    def to_xml(self, parent: ET.Element) -> ET.Element:
        define_element = ET.SubElement(
            parent, 
            f"{{{RELAXNG_NS}}}element",
            {
                "created-at": self.created_at,
                "last-changed": self.last_changed,
                "id": self.uuid,
                "name": self.name,
            },
        )

        # Names in languages
        for name in self.names:
            name.to_xml(define_element)

        self.annotations.to_xml(define_element)

        for optional in self.optionals:
            optional.to_xml(define_element)

        # Permisions
        for permission in self.permissions:
            permission.to_xml(define_element)

        return define_element