from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Iterable, Tuple, cast

from app.schemas.rapla.schema_rapla_permision import RaplaPermission


@dataclass
class SchemaInterfaceRaplaResourc(ABC):
    uuid: str
    owner: str
    created_at: str
    last_changed: str
    last_changed_by: str

    permissions: list[RaplaPermission] = field(default_factory=lambda: cast(list[RaplaPermission], []))

    @abstractmethod
    def to_xml(self, parent: ET.Element) -> ET.Element:
        """Serialize this resource into the given parent XML element."""
        raise NotImplementedError

    def _add_permissions(self, parent: ET.Element) -> None:
        # Permisions
        for permission in self.permissions:
            permission.to_xml(parent) 

    def _add_common_metadata(self, el: ET.Element) -> None:
        """Add the common metadata fields to the given element."""
        # write all common metadata as attributes on the element
        for tag, value in self._common_metadata_items():
            el.set(tag, value)

    def _common_metadata_items(self) -> Iterable[Tuple[str, str]]:
        return (
            ("uuid", self.uuid),
            ("owner", self.owner),
            ("created_at", self.created_at),
            ("last_changed", self.last_changed),
            ("last_changed_by", self.last_changed_by),
        )
