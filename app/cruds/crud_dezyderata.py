from datetime import date, datetime, timezone, timedelta
from typing import List, Optional, Set, cast
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.model_day import Day
from app.models.model_dezyderata import Dezyderata
from app.models.model_semestr import Semestr
from app.schemas.dezyderata import DezyderataCreate, SemestrCreate

# RAPLA Schemas
from app.schemas.rapla.reservations.schema_rapla_reservation_dezyderata import SchemaRaplaReservationDezyerata
from app.schemas.rapla.reservations.schema_rapla_apontment import SchemaRaplaApointment
from app.schemas.rapla.schema_rapla_reservations import SchemaRaplaReservations
from app.schemas.rapla.schema_rapla_permision import RaplaPermission
from app.schemas.rapla.reservations.schema_rapla_repeating import SchemaRaplaRepeating

# RAPLA Cruds
from app.cruds.rapla.crud_rapla_app_user_to_resourc import get_resorsc_by_user_id
from app.cruds.rapla.crud_rapla_users import get_first_rapla_users_by_username
from app.cruds.rapla.rapla_format_datetime import format_rapla_datetime

# ----- Semestr CRUD -----
# NOTE: This should be in seprate crude file for Semestr
def get_semestry(db: Session) -> List[Semestr]:
    return db.query(Semestr).order_by(Semestr.data_rozpoczecia.desc()).all()


def get_semestr_by_id(db: Session, semestr_id: int) -> Optional[Semestr]:
    return db.query(Semestr).filter(Semestr.id == semestr_id).first()


def get_current_semestr(db: Session, current_date: date | None= None) -> Optional[Semestr]:
    if current_date is None:
        current_date = date.today()
    return db.query(Semestr).filter(
        Semestr.data_rozpoczecia <= current_date,
        Semestr.data_zakonczenia >= current_date
    ).first()

# NOTE: Chenge this to field to field insted of payload
def create_semestr(db: Session, payload: SemestrCreate) -> Semestr:
    semestr = Semestr(
        data_rozpoczecia=payload.data_rozpoczecia,
        data_zakonczenia=payload.data_zakonczenia,
        nazwa=payload.nazwa
    )
    db.add(semestr)
    db.commit()
    db.refresh(semestr)
    return semestr

# NOTE: Need this by id
def delete_semestr(db: Session, semestr: Semestr) -> None:
    db.delete(semestr)
    db.commit()

# NOTE: This should be in seprate crude file for days
def get_days(db: Session) -> List[Day]:
    return db.query(Day).order_by(Day.id.asc()).all()

def get_day_by_id(db: Session, day_id: int) -> Day:
    return db.query(Day).filter(Day.id == day_id).first()

# NOTE: This should be in seprate crude file for days
def get_valid_day_ids(db: Session) -> Set[int]:
    return {day.id for day in get_days(db)}

def get_first_day(start: datetime, day_id: int) -> datetime:
    days_ahead = ( (day_id - 1) - start.weekday()) % 7
    return start + timedelta(days = days_ahead)


# ----- Dezyderata CRUD -----

def get_dezyderaty(db: Session, user_id: Optional[int] = None, semestr_id: Optional[int] = None) -> List[Dezyderata]:
    query = db.query(Dezyderata)
    if user_id is not None:
        query = query.filter(Dezyderata.user_id == user_id)
    if semestr_id is not None:
        query = query.filter(Dezyderata.semestr_id == semestr_id)
    return query.order_by(Dezyderata.data_od.desc(), Dezyderata.day_id.asc(), Dezyderata.from_hour.asc()).all()


def get_all_dezyderaty(db: Session) -> List[Dezyderata]:
    return db.query(Dezyderata).all()


def get_dezyderata_by_id(db: Session, dezyderata_id: int) -> Optional[Dezyderata]:
    return db.query(Dezyderata).filter(Dezyderata.id == dezyderata_id).first()

# NOTE: For what use is this
def replace_dezyderata_for_week(db: Session, user_id: int, payload: DezyderataCreate) -> List[Dezyderata]:
    db.query(Dezyderata).filter(
        Dezyderata.user_id == user_id,
        Dezyderata.data_od == payload.data_od,
        Dezyderata.data_do == payload.data_do,
        Dezyderata.semestr_id == payload.semestr_id,
    ).delete(synchronize_session=False)

    created_items: List[Dezyderata] = []
    for entry in payload.entries:
        created = Dezyderata(
            user_id=user_id,
            data_od=payload.data_od,
            data_do=payload.data_do,
            semestr_id=payload.semestr_id,
            day_id=entry.day_id,
            from_hour=entry.from_hour,
            to_hour=entry.to_hour + 1,
            is_available=entry.is_available,
        )
        db.add(created)
        created_items.append(created)

    db.commit()
    for item in created_items:
        db.refresh(item)

    return created_items


def delete_dezyderata(db: Session, dezyderata: Dezyderata) -> None:
    db.delete(dezyderata)
    db.commit()

# NOTE: Stop constracting JSON by hand use response class
def map_dezyderata_to_response(dezyderata: Dezyderata) -> dict:
    return {
        "id": dezyderata.id,
        "user_id": dezyderata.user_id,
        "data_od": dezyderata.data_od,
        "data_do": dezyderata.data_do,
        "semestr_id": dezyderata.semestr_id,
        "day_id": dezyderata.day_id,
        "from_hour": dezyderata.from_hour,
        "to_hour": dezyderata.to_hour,
        "is_available": dezyderata.is_available,
        "day_name": dezyderata.day.name if dezyderata.day else None,
        "semestr_nazwa": dezyderata.semestr.nazwa if dezyderata.semestr else None
    }

# NOTE: Stop constracting JSON by hand use response class. Move to crude semestr
def map_semestr_to_response(semestr: Semestr) -> dict:
    return {
        "id": semestr.id,
        "data_rozpoczecia": semestr.data_rozpoczecia,
        "data_zakonczenia": semestr.data_zakonczenia,
        "nazwa": semestr.nazwa
    }

# Needed for RAPLA conversion
# NOTE: Not done.
# FIXME:
# BUG: One for whole semester
def dezyderaty_to_schema(db: Session) -> SchemaRaplaReservations:
    list_of_model_dezyderata = get_all_dezyderaty(db)
    owner = get_first_rapla_users_by_username(db, "system")
    owner_uuid = owner.uuid if owner is not None else ""

    now = datetime.now(timezone.utc)
    created_at = now.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    last_changed = created_at

    list_of_dezyderat_schema: list[SchemaRaplaReservationDezyerata] = []
    for model_dezyderata in list_of_model_dezyderata:
        user_id = model_dezyderata.user_id
        resorc_user_data = get_resorsc_by_user_id(db, cast(int, user_id))
        semester = get_semestr_by_id( db,  cast( int, model_dezyderata.semestr_id ) )

        allocate: list[str] = []
        # Adding person
        if resorc_user_data is not None and getattr(resorc_user_data, "uuid", None):
            allocate.append( cast( str, resorc_user_data.uuid ) )

        repiting = SchemaRaplaRepeating(
            type = "weekly",
            end_date = format_rapla_datetime( cast(datetime, semester.data_zakonczenia ) ),
        )

        apointment = SchemaRaplaApointment(
            uuid=str(uuid4()),
            start_date=format_rapla_datetime(get_first_day(cast(datetime, semester.data_rozpoczecia), cast(int, model_dezyderata.day_id))),
            start_time=f"{int(model_dezyderata.from_hour):02d}:00:00",
            end_date=format_rapla_datetime(get_first_day(cast(datetime, semester.data_rozpoczecia), cast(int, model_dezyderata.day_id))),
            end_time=f"{int(model_dezyderata.to_hour):02d}:00:00",
            repeating=repiting,
        )

        res_uuid = str(uuid4())
        dezyd = SchemaRaplaReservationDezyerata(
            uuid = res_uuid,
            owner = cast( str, owner_uuid ),
            created_at = created_at,
            last_changed = last_changed,
            last_changed_by = cast( str, owner_uuid ),

            apointment=apointment,

            name="Dezyderata",
            color="#FF0000",

            allocate=allocate,
            permissions=[RaplaPermission(group="category[key='read-events-from-others']", access="read")],
        )

        list_of_dezyderat_schema.append(dezyd)

    return SchemaRaplaReservations(list_of_dezyderat_schema)
