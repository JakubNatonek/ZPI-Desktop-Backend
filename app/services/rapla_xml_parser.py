"""Parser for Rapla XML files.

Extracts reservation/appointment data together with resolved resource names
(rooms, teachers, semesters) referenced via <rapla:allocate idref="...">.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional


# --- Rapla XML namespaces ---------------------------------------------------
_RAPLA     = "http://rapla.sourceforge.net/rapla"
_DYNATT    = "http://rapla.sourceforge.net/dynamictype"
_EXTENSION = "http://rapla.sourceforge.net/extension"

_TAG_RESERVATION  = f"{{{_RAPLA}}}reservation"
_TAG_APPOINTMENT  = f"{{{_RAPLA}}}appointment"
_TAG_REPEATING    = f"{{{_RAPLA}}}repeating"
_TAG_ALLOCATE     = f"{{{_RAPLA}}}allocate"
_TAG_RESOURCE     = f"{{{_RAPLA}}}resource"
_TAG_PERSON       = f"{{{_RAPLA}}}person"
_TAG_EXTENSION    = f"{{{_RAPLA}}}extension"
_TAG_DYNATT_NAME  = f"{{{_DYNATT}}}name"
_TAG_DYNATT_COLOR = f"{{{_DYNATT}}}color"
_TAG_DYNATT_DEZYDERATA = f"{{{_DYNATT}}}dezyderata"

# room fields
_TAG_ROOM         = f"{{{_DYNATT}}}room"
_TAG_ROOM_NUMBER  = f"{{{_DYNATT}}}room_number"

# teacher fields
_TAG_NAUCZYCIEL   = f"{{{_DYNATT}}}nauczyciel"
_TAG_IMIE         = f"{{{_DYNATT}}}imie"
_TAG_NAZWISKO     = f"{{{_DYNATT}}}nazwisko"

# semester / period fields
_TAG_PERIOD       = f"{{{_EXTENSION}}}period"
_TAG_PERIOD_NAME  = f"{{{_EXTENSION}}}name"


@dataclass
class ParsedReservation:
    uuid: str
    name: Optional[str] = None
    color: Optional[str] = None

    # appointment (first one only)
    start_date: Optional[str] = None
    start_time: Optional[str] = None
    end_date: Optional[str] = None
    end_time: Optional[str] = None

    # repeating
    repeating_type: Optional[str] = None
    repeating_end_date: Optional[str] = None

    # raw resource UUID references
    allocate: list[str] = field(default_factory=list)

    # resolved human-readable names (populated during parsing)
    room_names: list[str] = field(default_factory=list)
    teacher_names: list[str] = field(default_factory=list)
    semester_names: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "color": self.color,
            "start_date": self.start_date,
            "start_time": self.start_time,
            "end_date": self.end_date,
            "end_time": self.end_time,
            "repeating_type": self.repeating_type,
            "repeating_end_date": self.repeating_end_date,
            "allocate": self.allocate,
            "room_names": self.room_names,
            "teacher_names": self.teacher_names,
            "semester_names": self.semester_names,
        }


def _strip_category_key(value: str) -> str:
    """Extract the key from a string like \"category[key='dr hab.']\". Returns value unchanged if it doesn't match."""
    if value.startswith("category[key='") and value.endswith("']"):
        return value[len("category[key='"):-2]
    return value


# ---------------------------------------------------------------------------
# Resource name extraction helpers
# ---------------------------------------------------------------------------

def _build_resource_map(root: ET.Element) -> dict[str, dict]:
    """Return a mapping uuid -> {type, name, ...} for all resource/person/extension elements."""
    result: dict[str, dict] = {}

    # --- Rooms: <rapla:resource id="..."><dynatt:room><dynatt:room_number>…
    for el in root.iter(_TAG_RESOURCE):
        uuid = el.get("id", "").strip()
        if not uuid:
            continue
        room_el = el.find(_TAG_ROOM)
        if room_el is not None:
            number_el   = room_el.find(_TAG_ROOM_NUMBER)
            seats_el    = room_el.find(f"{{{_DYNATT}}}seats")
            rtype_el    = room_el.find(f"{{{_DYNATT}}}room_type")
            room_number = (number_el.text or "").strip() if number_el is not None else ""
            seats       = (seats_el.text or "").strip()  if seats_el  is not None else ""
            rtype       = _strip_category_key((rtype_el.text or "").strip()) if rtype_el is not None else ""
            label_parts = [p for p in [room_number, rtype, (f"{seats} miejsc" if seats else "")] if p]
            result[uuid] = {"type": "room", "name": ", ".join(label_parts) if label_parts else uuid}

    # --- Teachers: <rapla:person id="..."><dynatt:nauczyciel>…
    for el in root.iter(_TAG_PERSON):
        uuid = el.get("id", "").strip()
        if not uuid:
            continue
        naucz_el = el.find(_TAG_NAUCZYCIEL)
        if naucz_el is not None:
            imie_el      = naucz_el.find(_TAG_IMIE)
            nazwisko_el  = naucz_el.find(_TAG_NAZWISKO)
            tytul_el     = naucz_el.find(f"{{{_DYNATT}}}tytul")
            wydzial_el   = naucz_el.find(f"{{{_DYNATT}}}wydzial")

            imie     = (imie_el.text     or "").strip() if imie_el     is not None else ""
            nazwisko = (nazwisko_el.text or "").strip() if nazwisko_el is not None else ""
            tytul    = _strip_category_key((tytul_el.text   or "").strip()) if tytul_el   is not None else ""
            wydzial  = _strip_category_key((wydzial_el.text or "").strip()) if wydzial_el is not None else ""

            # Rapla-like label: surname first, then first name, title and department.
            full = " ".join(filter(None, [nazwisko, imie, tytul, wydzial])) or uuid
            result[uuid] = {"type": "teacher", "name": full, "department": wydzial}

    # --- Semesters: <rapla:extension id="..."><ext:period><ext:name>…
    for el in root.iter(_TAG_EXTENSION):
        uuid = el.get("id", "").strip()
        if not uuid:
            continue
        period_el = el.find(_TAG_PERIOD)
        if period_el is not None:
            name_el  = period_el.find(_TAG_PERIOD_NAME)
            start_el = period_el.find(f"{{{_EXTENSION}}}start")
            end_el   = period_el.find(f"{{{_EXTENSION}}}end")
            sem_name = (name_el.text  or "").strip() if name_el  is not None else ""
            sem_start = (start_el.text or "").strip() if start_el is not None else ""
            sem_end   = (end_el.text   or "").strip() if end_el   is not None else ""
            label = sem_name or (f"{sem_start}–{sem_end}" if sem_start else uuid)
            result[uuid] = {"type": "semester", "name": label}

    return result


# ---------------------------------------------------------------------------
# Main parse function
# ---------------------------------------------------------------------------

def parse_rapla_reservations(xml_text: str) -> list[ParsedReservation]:
    """Parse a Rapla XML string and return all reservation entries.

    Resource UUIDs in <rapla:allocate> are resolved to human-readable names
    and stored in room_names / teacher_names / semester_names lists.
    """
    root = ET.fromstring(xml_text)

    resource_map = _build_resource_map(root)

    results: list[ParsedReservation] = []

    for res_el in root.iter(_TAG_RESERVATION):
        uuid = res_el.get("id", "").strip()
        if not uuid:
            continue

        parsed = ParsedReservation(uuid=uuid)

        # Extract the first <rapla:appointment>
        appt_el = res_el.find(_TAG_APPOINTMENT)
        if appt_el is not None:
            parsed.start_date = appt_el.get("start-date")
            parsed.start_time = appt_el.get("start-time")
            parsed.end_date   = appt_el.get("end-date")
            parsed.end_time   = appt_el.get("end-time")

            rep_el = appt_el.find(_TAG_REPEATING)
            if rep_el is not None:
                parsed.repeating_type     = rep_el.get("type")
                parsed.repeating_end_date = rep_el.get("end-date")

        # Extract <rapla:allocate idref="..."> and resolve names
        for alloc_el in res_el.findall(_TAG_ALLOCATE):
            idref = alloc_el.get("idref", "").strip()
            if not idref:
                continue
            parsed.allocate.append(idref)
            resource = resource_map.get(idref)
            if resource:
                rtype = resource.get("type")
                rname = resource.get("name", idref)
                if rtype == "room":
                    parsed.room_names.append(rname)
                elif rtype == "teacher":
                    parsed.teacher_names.append(rname)
                elif rtype == "semester":
                    parsed.semester_names.append(rname)

        # Extract dezyderata-specific fields first.
        dezyderata_el = res_el.find(_TAG_DYNATT_DEZYDERATA)
        if dezyderata_el is not None:
            name_el = dezyderata_el.find(_TAG_DYNATT_NAME)
            color_el = dezyderata_el.find(_TAG_DYNATT_COLOR)
            if name_el is not None and name_el.text:
                parsed.name = name_el.text.strip()
            if color_el is not None and color_el.text:
                parsed.color = color_el.text.strip()

        # Fallback: extract human-readable name from any <dynatt:*> child.
        for dynatt_child in res_el:
            name_el = dynatt_child.find(_TAG_DYNATT_NAME)
            if parsed.name is None and name_el is not None and name_el.text:
                parsed.name = name_el.text.strip()
            if parsed.name is not None:
                break

        results.append(parsed)

    return results

