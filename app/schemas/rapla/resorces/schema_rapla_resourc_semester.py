from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import Iterable, Tuple, cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS, EXTENSION_NS
from app.schemas.rapla.schema_rapla_permision import RaplaPermission


@dataclass
class SchemaRaplaResourcSemester:
    uuid: str
    owner: str
    created_at: str
    last_changed: str
    last_changed_by: str

    name: str
    start: str
    end: str

    permissions: list[RaplaPermission] = field(default_factory=lambda: cast(list[RaplaPermission], []))


    def to_xml(self, parent: ET.Element) -> ET.Element:
        extension = ET.SubElement(
            parent,
            f"{{{RAPLA_NS}}}extension",
        )
        # add common metadata
        self._add_common_metadata(extension)

        # Period (extension namespace) and its children
        period = ET.SubElement(
            extension,
            f"{{{EXTENSION_NS}}}period",
        )

        name_el = ET.SubElement(period, f"{{{EXTENSION_NS}}}name")
        name_el.text = self.name

        start_el = ET.SubElement(period, f"{{{EXTENSION_NS}}}start")
        start_el.text = self.start

        end_el = ET.SubElement(period, f"{{{EXTENSION_NS}}}end")
        end_el.text = self.end

        # permissions should follow the period element (matches example)
        self._add_permissions(extension)

        return extension

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