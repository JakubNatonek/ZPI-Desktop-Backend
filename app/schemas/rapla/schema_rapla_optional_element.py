from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import cast, List

from app.schemas.rapla.rapla_namespaces import RELAXNG_NS, RAPLA_NS

from app.schemas.rapla.schema_rapla_language_name import RaplaLanguageName
from app.schemas.rapla.schema_rapla_data_type import RaplaDataType
from app.schemas.rapla.schema_rapla_constraint import RaplaConstraint


@dataclass
class OptionalElement:
    name: str
    default_value: str
    data_type: RaplaDataType
    names: List[RaplaLanguageName] = field(default_factory=lambda: cast(List[RaplaLanguageName], []))
    constraints: List[RaplaConstraint] = field(default_factory=lambda: cast(List[RaplaConstraint], []))

    def to_xml(self, parent: ET.Element) -> ET.Element:
        optional_element = ET.SubElement(
            parent, 
            f"{{{RELAXNG_NS}}}element",
            {
                "name": self.name,
            },
        )

        # Names in languages
        for name in self.names:
            name.to_xml(optional_element)

        # type of data
        self.data_type.to_xml(optional_element)

        # constrains
        for constraint in self.constraints:
            constraint.to_xml(optional_element)


        # defoult value
        default_value_element = ET.SubElement(
            optional_element, 
            f"{{{RAPLA_NS}}}default",
        )
        default_value_element.text = self.default_value

        return optional_element