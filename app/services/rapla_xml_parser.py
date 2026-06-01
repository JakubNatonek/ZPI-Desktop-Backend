from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

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
_TAG_DYNATT_ZAJENCIA   = f"{{{_DYNATT}}}zajencia"
_TAG_DYNATT_PRZEDMIOT  = f"{{{_DYNATT}}}przedmiot"
_TAG_DYNATT_GRUPA      = f"{{{_DYNATT}}}grupa" 

_TAG_ROOM         = f"{{{_DYNATT}}}room"
_TAG_ROOM_NUMBER  = f"{{{_DYNATT}}}room_number"

_TAG_NAUCZYCIEL   = f"{{{_DYNATT}}}nauczyciel"
_TAG_IMIE         = f"{{{_DYNATT}}}imie"
_TAG_NAZWISKO     = f"{{{_DYNATT}}}nazwisko"

_TAG_PERIOD       = f"{{{_EXTENSION}}}period"
_TAG_PERIOD_NAME  = f"{{{_EXTENSION}}}name"


@dataclass
class ParsedReservation:
    uuid: str           
    name: Optional[str] = None
    color: Optional[str] = None

    reservation_type: str = "dezyderata"
    reservation_uuid: Optional[str] = None   
    activity_type: Optional[str] = None      # 'wyklady', 'laboratoria'

    start_date: Optional[str] = None
    start_time: Optional[str] = None
    end_date: Optional[str] = None
    end_time: Optional[str] = None

    repeating_type: Optional[str] = None
    repeating_end_date: Optional[str] = None

    allocate: list[str] = field(default_factory=list)

    room_names: list[str] = field(default_factory=list)
    teacher_names: list[str] = field(default_factory=list)
    semester_names: list[str] = field(default_factory=list)
    group_names: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "color": self.color,
            "reservation_type": self.reservation_type,
            "reservation_uuid": self.reservation_uuid,
            "activity_type": self.activity_type,
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
            "group_names": self.group_names,
        }


def _strip_category_key(value: str) -> str:
    """Extract the key from a string like \"category[key='dr hab.']\". Returns value unchanged if it doesn't match."""
    if value.startswith("category[key='") and value.endswith("']"):
        return value[len("category[key='"):-2]
    return value


def _build_resource_map(root: ET.Element) -> dict[str, dict]:
    """Return a mapping uuid -> {type, name, ...} for all resource/person/extension elements."""
    result: dict[str, dict] = {}

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
        else:
            przedmiot_el = el.find(_TAG_DYNATT_PRZEDMIOT)
            if przedmiot_el is not None:
                name_el     = przedmiot_el.find(_TAG_DYNATT_NAME)
                activity_el = przedmiot_el.find(f"{{{_DYNATT}}}activity")
                subject_name   = (name_el.text     or "").strip() if name_el     is not None else ""
                activity_type  = _strip_category_key((activity_el.text or "").strip()) if activity_el is not None else ""
                result[uuid] = {"type": "subject", "name": subject_name or uuid, "activity": activity_type}
            else:
                grupa_el = el.find(_TAG_DYNATT_GRUPA)
                if grupa_el is not None:
                    name_el = grupa_el.find(_TAG_DYNATT_NAME)
                    group_name = (name_el.text or "").strip() if name_el is not None else ""
                    result[uuid] = {"type": "group", "name": group_name or uuid}

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

            full = " ".join(filter(None, [nazwisko, imie, tytul, wydzial])) or uuid
            result[uuid] = {"type": "teacher", "name": full, "department": wydzial}

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


def parse_rapla_reservations(xml_text: str) -> list[ParsedReservation]:

    root = ET.fromstring(xml_text)

    resource_map = _build_resource_map(root)

    results: list[ParsedReservation] = []

    for res_el in root.iter(_TAG_RESERVATION):
        res_uuid = res_el.get("id", "").strip()
        if not res_uuid:
            continue

        dezyderata_el = res_el.find(_TAG_DYNATT_DEZYDERATA)
        zajencia_el   = res_el.find(_TAG_DYNATT_ZAJENCIA)
        res_type = "zajencia" if zajencia_el is not None else "dezyderata"

        shared_name: Optional[str] = None
        shared_color: Optional[str] = None
        shared_activity: Optional[str] = None

        if dezyderata_el is not None:
            name_el  = dezyderata_el.find(_TAG_DYNATT_NAME)
            color_el = dezyderata_el.find(_TAG_DYNATT_COLOR)
            if name_el is not None and name_el.text:
                shared_name = name_el.text.strip()
            if color_el is not None and color_el.text:
                shared_color = color_el.text.strip()
        elif zajencia_el is not None:
            name_el = zajencia_el.find(_TAG_DYNATT_NAME)
            if name_el is not None and name_el.text:
                subject_uuid = name_el.text.strip()
                subject_resource = resource_map.get(subject_uuid)
                if subject_resource and subject_resource.get("type") == "subject":
                    shared_name     = subject_resource["name"]
                    shared_activity = subject_resource.get("activity") or None
                else:
                    shared_name = subject_uuid  

        seen_alloc:    dict[str, None] = {}
        seen_rooms:    dict[str, None] = {}
        seen_teachers: dict[str, None] = {}
        seen_semesters: dict[str, None] = {}
        seen_groups:   dict[str, None] = {}

        for alloc_el in res_el.iter(_TAG_ALLOCATE):
            idref = alloc_el.get("idref", "").strip()
            if not idref:
                continue
            seen_alloc[idref] = None
            resource = resource_map.get(idref)
            if resource:
                rtype = resource.get("type")
                rname = resource.get("name", idref)
                if rtype == "room":
                    seen_rooms[rname] = None
                elif rtype == "teacher":
                    seen_teachers[rname] = None
                elif rtype == "semester":
                    seen_semesters[rname] = None
                elif rtype == "group":
                    seen_groups[rname] = None

        shared_allocate      = list(seen_alloc)
        shared_room_names    = list(seen_rooms)
        shared_teacher_names = list(seen_teachers)
        shared_semester_names = list(seen_semesters)
        shared_group_names   = list(seen_groups)

        appt_els = res_el.findall(_TAG_APPOINTMENT)
        if not appt_els:
            continue

        for appt_el in appt_els:
            appt_uuid = appt_el.get("id", "").strip()
            if not appt_uuid:
                continue

            rep_el = appt_el.find(_TAG_REPEATING)

            parsed = ParsedReservation(
                uuid             = appt_uuid,
                reservation_uuid = res_uuid,
                name             = shared_name,
                color            = shared_color,
                reservation_type = res_type,
                activity_type    = shared_activity,
                start_date       = appt_el.get("start-date"),
                start_time       = appt_el.get("start-time"),
                end_date         = appt_el.get("end-date"),
                end_time         = appt_el.get("end-time"),
                repeating_type     = rep_el.get("type")     if rep_el is not None else None,
                repeating_end_date = rep_el.get("end-date") if rep_el is not None else None,
                allocate       = shared_allocate,
                room_names     = shared_room_names,
                teacher_names  = shared_teacher_names,
                semester_names = shared_semester_names,
                group_names    = shared_group_names,
            )
            results.append(parsed)

    return results

