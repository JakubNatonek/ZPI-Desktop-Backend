from datetime import date
from typing import cast

from sqlalchemy.orm import Session

from app.models.model_semestr import Semestr

# Rapla helpers: create resource and mapping for each semester
from app.models.rapla.model_rapla_user import RaplaUser as RaplaUserModel
from app.cruds.rapla.crud_rapla_resourc import create_resourc
from app.cruds.rapla.crud_rapla_semester_to_resourc import (
    get_resorsc_by_semestr_id,
    create_semester_to_resourc_mapping,
)
from app.cruds.rapla.crud_rapla_permission import get_permission_by_access, create_permission
from app.cruds.rapla.crud_rapla_permission_for_resourc import create_permission_for_resourc
from app.cruds.rapla.crud_rapla_users import  get_first_rapla_users_by_username

def ensure_rapla_resource_for_semester(db: Session, sem_row: Semestr) -> None:
    # Try to find rapla "system" user to use as owner for created resources
    rapla_system = get_first_rapla_users_by_username(db, "system")
    owner_uuid:str = ""
    if rapla_system is not None:
        owner_uuid = cast(str, rapla_system.uuid)
    try:
        existing_res = get_resorsc_by_semestr_id(db, cast(int, sem_row.id) )
        if existing_res is None:
            res = create_resourc(db, owner=owner_uuid)
            create_semester_to_resourc_mapping(db, cast(int, sem_row.id), cast( int, res.id))

            perm = get_permission_by_access(db, access="read")
            if perm is None:
                perm = create_permission(db, access="read")
            create_permission_for_resourc(db, cast(int, res.id), cast(int, perm.id))
            print(f"Created Rapla resource id={res.id} for semester '{sem_row.nazwa}'")
        else:
            perm = get_permission_by_access(db, access="read")
            if perm is None:
                perm = create_permission(db, access="read")
            try:
                create_permission_for_resourc(db, cast(int, existing_res.id), cast(int, perm.id))
            except Exception:
                pass
    except Exception as e:
        print(f"Failed to ensure Rapla resource for semester '{sem_row.nazwa}': {e}")


def seed_semesters(db: Session):
    """Seed semesters table with sample data and create Rapla resources/mappings."""
    semesters = [
        {"nazwa": "Semestr zimowy 2025/2026", "data_rozpoczecia": date(2025, 10, 1), "data_zakonczenia": date(2026, 2, 15)},
        {"nazwa": "Semestr letni 2025/2026", "data_rozpoczecia": date(2026, 2, 17), "data_zakonczenia": date(2026, 6, 30)},
        {"nazwa": "Semestr zimowy 2026/2027", "data_rozpoczecia": date(2026, 10, 1), "data_zakonczenia": date(2027, 2, 15)},
    ]



    created_count = 0
    for sem in semesters:
        sem_row = db.query(Semestr).filter_by(
            nazwa=sem["nazwa"],
            data_rozpoczecia=sem["data_rozpoczecia"],
            data_zakonczenia=sem["data_zakonczenia"],
        ).first()
        if sem_row is None:
            sem_row = Semestr(**sem)
            db.add(sem_row)
            db.commit()
            db.refresh(sem_row)
            created_count += 1

        # Ensure a Rapla resource and mapping exist for this semester
        ensure_rapla_resource_for_semester(db, sem_row)

    print(f"Semesters seeded. Added: {created_count}")