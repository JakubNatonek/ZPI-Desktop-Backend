from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import Optional, Iterable, Tuple, cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS, DYNATT_NS
from app.schemas.rapla.schema_rapla_permision import RaplaPermission


@dataclass
class SchemaRaplaResourcNauczyciel:
    uuid: str
    owner: str
    created_at: str
    last_changed: str
    last_changed_by: str

    permissions: list[RaplaPermission] = field(default_factory=lambda: cast(list[RaplaPermission], []))

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    departments: list[str] | None = None

    def to_xml(self, parent: ET.Element) -> ET.Element:
        person = ET.SubElement(
            parent,
            f"{{{RAPLA_NS}}}person",
        )
        # add common metadata and permissions
        self._add_common_metadata(person)
        self._add_permissions(person)

        nauczyciel = ET.SubElement(
            person,
            f"{{{DYNATT_NS}}}nauczyciel",
        )

        if self.first_name:
            first_name = ET.SubElement(nauczyciel, f"{{{DYNATT_NS}}}imie")
            first_name.text = self.first_name
        if self.last_name:
            last_name = ET.SubElement(nauczyciel, f"{{{DYNATT_NS}}}nazwisko")
            last_name.text = self.last_name
        if self.title:
            title = ET.SubElement(nauczyciel, f"{{{DYNATT_NS}}}tytul")
            title.text = f"category[key='{self.title}']"
        if self.departments:
            for department in self.departments:
                depatment_el = ET.SubElement(nauczyciel, f"{{{DYNATT_NS}}}wydzial")
                depatment_el.text = f"category[key='{department}']"

        return person

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
            ("created_at", self.created_at),
            ("last_changed", self.last_changed),
            ("last_changed_by", self.last_changed_by),
        )