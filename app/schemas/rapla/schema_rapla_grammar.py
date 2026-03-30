from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import cast

from app.schemas.rapla.rapla_namespaces import RELAXNG_NS

from app.schemas.rapla.schema_rapla_define import Define


##
# @file schema_rapla_grammar.py
# @brief Helpers to render RelaxNG grammar elements for Rapla schemas.
#
# This module aggregates `Define` objects and renders them using
# ElementTree with the RelaxNG namespace.
@dataclass
class RaplaGrammar:

    ##
    # @brief Container for RelaxNG `define` blocks.
    # @var defines List of `Define` objects that will be rendered inside the
    # RelaxNG `grammar` element. Defaults to an empty list.
    defines: list[Define] = field(default_factory=lambda: cast(list[Define], []))

    def to_xml(self, parent: ET.Element) -> ET.Element:

        ##
        # @brief Append a RelaxNG <grammar> element containing all defines.
        # @param parent Parent XML element to append the <grammar> element to.
        # @return The newly created <grammar> Element.

        grammar_el = ET.SubElement(parent, f"{{{RELAXNG_NS}}}grammar")
        for define_el in self.defines:
            define_el.to_xml(grammar_el)

        self.start_element_to_xml(grammar_el)
        return grammar_el

    
    def start_element_to_xml(self, parent: ET.Element) -> ET.Element:

        ##
        # @brief Append a RelaxNG <start> element with a <choice> of refs.
        # @param parent Parent XML element to append the <start> element to.
        # @return The newly created <start> Element.

        relax_start = ET.SubElement(parent, f"{{{RELAXNG_NS}}}start")
        relax_choice = ET.SubElement(relax_start, f"{{{RELAXNG_NS}}}choice")

        for define in self.defines:
            ET.SubElement(
                relax_choice,
                f"{{{RELAXNG_NS}}}ref",
                {"name": define.name},
            )

        return relax_start