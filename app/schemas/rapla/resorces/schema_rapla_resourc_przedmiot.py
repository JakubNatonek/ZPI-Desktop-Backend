from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import Iterable, Optional, Tuple, cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS, DYNATT_NS
from app.schemas.rapla.schema_rapla_permision import RaplaPermission


@dataclass
class SchemaRaplaResourcPrzedmiot:
    uuid: str
    owner: str
    created_at: str
    last_changed: str
    last_changed_by: str

    permissions: list[RaplaPermission] = field(default_factory=lambda: cast(list[RaplaPermission], []))

    name: Optional[str] = None
    activity: Optional[str] = None
    room_properties: Optional[str] = None
    field_of_study_abbrevation: Optional[str] = None
    field_of_study_year: Optional[int] = None

    def to_xml(self, parent: ET.Element) -> ET.Element:
        resource = ET.SubElement(
            parent,
            f"{{{RAPLA_NS}}}resource",
        )
        self._add_common_metadata(resource)
        self._add_permissions(resource)

        przedmiot = ET.SubElement(
            resource,
            f"{{{DYNATT_NS}}}przedmiot",
        )

        if self.name:
            name_el = ET.SubElement(przedmiot, f"{{{DYNATT_NS}}}name")
            name_el.text = self.name

        if self.activity:
            activity_el = ET.SubElement(przedmiot, f"{{{DYNATT_NS}}}activity")
            activity_el.text = f"category[key='{self.activity}']"

        if self.room_properties:
            room_properties_el = ET.SubElement(przedmiot, f"{{{DYNATT_NS}}}room_properties")
            room_properties_el.text = self.room_properties

        if self.field_of_study_abbrevation:
            abbrev_el = ET.SubElement(przedmiot, f"{{{DYNATT_NS}}}field_of_study_abbrevation")
            abbrev_el.text = self.field_of_study_abbrevation

        if self.field_of_study_year is not None:
            year_el = ET.SubElement(przedmiot, f"{{{DYNATT_NS}}}field_of_study_year")
            year_el.text = str(self.field_of_study_year)

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
