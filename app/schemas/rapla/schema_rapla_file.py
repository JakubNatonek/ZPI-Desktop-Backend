from dataclasses import dataclass, field
import xml.etree.ElementTree as ET

from app.schemas.rapla.rapla_namespaces import (
    NSMAP,
    RAPLA_NS,
    RAPLA_VERSION,
)
from app.schemas.rapla.schema_rapla_categories import RaplaCategories
from app.schemas.rapla.schema_rapla_users import RaplaUsers
from app.schemas.rapla.schema_rapla_grammar import RaplaGrammar
from app.schemas.rapla.schema_rapla_resources import SchemaRaplaResources
from app.schemas.rapla.schema_rapla_reservations import SchemaRaplaReservations

@dataclass
class RaplaFile:
    version: str = RAPLA_VERSION
    users: RaplaUsers = field(default_factory=RaplaUsers)
    categories: RaplaCategories = field(default_factory=RaplaCategories)
    grammar: RaplaGrammar = field(default_factory=RaplaGrammar)

    # preferences: PreferencesSection = field(default_factory=PreferencesSection)

    resources: SchemaRaplaResources = field(default_factory=SchemaRaplaResources)

    # reservations: list[Reservation] = field(default_factory=lambda: cast(list[Reservation], []))
    reservations: SchemaRaplaReservations = field(default_factory=SchemaRaplaReservations)
    # importexports: ImportExportsSection = field(default_factory=ImportExportsSection)

    ##
    # @brief Serialize Rapla root data to XML.
    # @details Registers known namespace prefixes from NSMAP and builds a
    #          namespaced <rapla:data> root element with the configured version.
    # @return UTF-8 XML document string with XML declaration.
    def to_xml(self) -> str:
        for prefix, uri in NSMAP.items():
            ET.register_namespace(prefix, uri)

        root = ET.Element(
            f"{{{RAPLA_NS}}}data",
            {
                "version": self.version,
            },
        )
        self.categories.to_xml(root)
        self.users.to_xml(root)
        self.grammar.to_xml(root)
        self.resources.to_xml(root)
        self.reservations.to_xml(root)
        ET.indent(root, space="    ")

        xml_bytes = ET.tostring(
            root,
            encoding="utf-8",
            xml_declaration=True,
            # short_empty_elements=False, # It should be chenge propabli
        )
        return xml_bytes.decode("utf-8")

    ##
    # @brief Save serialized Rapla XML to a file.
    # @param path Target file path where XML should be written.
    def save_to_file(self, path: str) -> None:
        xml_text = self.to_xml()
        with open(path, "w", encoding="utf-8", newline="\n") as file:
            file.write(xml_text)
