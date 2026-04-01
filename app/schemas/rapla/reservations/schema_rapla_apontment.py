from dataclasses import dataclass
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import RAPLA_NS


@dataclass
class SchemaRaplaApointment:
    uuid: str
    start_date: str
    start_time: str
    end_date: str
    end_time: str

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

        return appointment
	
