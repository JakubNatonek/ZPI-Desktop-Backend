from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import cast

from app.schemas.rapla.rapla_namespaces import RAPLA_NS

from app.schemas.rapla.reservations.schema_rapla_reservation_dezyderata import SchemaRaplaReservationDezyerata


@dataclass
class SchemaRaplaReservations:

    dezyderata: list[SchemaRaplaReservationDezyerata] = field(default_factory=lambda: cast(list[SchemaRaplaReservationDezyerata], []))

    def to_xml(self, parent: ET.Element) -> ET.Element:
        rezervation_el = ET.SubElement(parent, f"{{{RAPLA_NS}}}reservations")
        for resourc_el in self.dezyderata:
            resourc_el.to_xml(rezervation_el)

        return rezervation_el
