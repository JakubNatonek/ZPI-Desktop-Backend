from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import cast, List, Optional

from app.schemas.rapla.rapla_namespaces import RELAXNG_NS, RAPLA_NS

from app.schemas.rapla.schema_rapla_language_name import RaplaLanguageName
from app.schemas.rapla.schema_rapla_data_type import RaplaDataType
from app.schemas.rapla.schema_rapla_constraint import RaplaConstraint
from app.schemas.rapla.schema_rapla_annotations import RaplaAnnotations


@dataclass
class OptionalElement:
    name: str
    data_type: RaplaDataType
    default_value: Optional[str] = None
    names: List[RaplaLanguageName] = field(default_factory=lambda: cast(List[RaplaLanguageName], []))
    constraints: Optional[List[RaplaConstraint]] | None = field(default_factory=lambda: cast(List[RaplaConstraint], []))
    annotations: Optional[RaplaAnnotations] | None = field(default_factory=lambda: RaplaAnnotations())

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


        if self.annotations is not None:
            self.annotations.to_xml(optional_element)

        # type of data
        self.data_type.to_xml(optional_element)

        # constraints
        if self.constraints is not None:
            for constraint in self.constraints:
                constraint.to_xml(optional_element)


        # default value
        if self.default_value is not None:
            default_value_element = ET.SubElement(
                optional_element, 
                f"{{{RAPLA_NS}}}default",
            )
            default_value_element.text = self.default_value

        return optional_element