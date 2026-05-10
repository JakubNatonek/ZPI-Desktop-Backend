from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import Iterable, Tuple, cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS, DYNATT_NS
from app.schemas.rapla.schema_rapla_permision import RaplaPermission


@dataclass
class SchemaRaplaResourcGrupa:
    uuid: str
    owner: str
    created_at: str
    last_changed: str
    last_changed_by: str

    name: str | None = None
    kierunek: str | None = None
    rok: str | None = None

    permissions: list[RaplaPermission] = field(default_factory=lambda: cast(list[RaplaPermission], []))

    def to_xml(self, parent: ET.Element) -> ET.Element:
        resource = ET.SubElement(parent, f"{{{RAPLA_NS}}}resource")
        self._add_common_metadata(resource)
        self._add_permissions(resource)

        grupa = ET.SubElement(resource, f"{{{DYNATT_NS}}}grupa")

        if self.name is not None:
            name_el = ET.SubElement(grupa, f"{{{DYNATT_NS}}}name")
            name_el.text = self.name

        if self.kierunek is not None:
            kierunek_el = ET.SubElement(grupa, f"{{{DYNATT_NS}}}kierunek")
            kierunek_el.text = self.kierunek

        if self.rok is not None:
            rok_el = ET.SubElement(grupa, f"{{{DYNATT_NS}}}rok")
            rok_el.text = self.rok

        return resource

    def _add_permissions(self, parent: ET.Element) -> None:
        for permission in self.permissions:
            permission.to_xml(parent)

    def _add_common_metadata(self, el: ET.Element) -> None:
        for tag, value in self._common_metadata_items():
            el.set(tag, value)

    def _common_metadata_items(self) -> Iterable[Tuple[str, str]]:
        return (
            ("id", self.uuid),
            ("owner", self.owner),
            ("created-at", self.created_at),
            ("last-changed", self.last_changed),
            ("last-changed-by", self.last_changed_by),
        )
