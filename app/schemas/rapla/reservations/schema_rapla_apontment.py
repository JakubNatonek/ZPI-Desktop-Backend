from dataclasses import dataclass, field
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import RAPLA_NS
from app.schemas.rapla.reservations.schema_rapla_repeating import SchemaRaplaRepeating

@dataclass
class SchemaRaplaApointment:
    uuid: str
    start_date: str
    start_time: str
    end_date: str
    end_time: str
    repeating: SchemaRaplaRepeating | None = None
    allocate: list[str] = field(default_factory=list)

    def to_xml(self, parent: ET.Element) -> ET.Element:
        appointment = ET.SubElement(
            parent,
            f"{{{RAPLA_NS}}}appointment",
            {
                "id": self.uuid,
                "start-date": self.start_date,
                "start-time": self.start_time,
                "end-date": self.end_date,
                "end-time": self.end_time,
            },
        )
        
        if self.repeating is not None:
            self.repeating.to_xml(appointment)

        for idref in (self.allocate or []):
            if idref:
                ET.SubElement(appointment, f"{{{RAPLA_NS}}}allocate", {"idref": idref})

        return appointment

