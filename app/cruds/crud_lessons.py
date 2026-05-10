from datetime import date, time, datetime, timezone
from typing import Optional, cast
from uuid import uuid4

from sqlalchemy.orm import Session

from app.cruds.rapla.crud_rapla_app_user_to_resourc import get_resorsc_by_user_id
from app.cruds.rapla.crud_rapla_room_to_resourc import get_resorsc_by_room_id
from app.cruds.rapla.crud_rapla_subject_to_resourc import get_resourc_by_subject_id
from app.cruds.rapla.crud_rapla_users import get_first_rapla_users_by_username
from app.cruds.rapla.rapla_format_datetime import format_rapla_date
from app.cruds.crud_subject_for_field_of_study import get_primary_field_of_study_for_subject
from app.cruds.crud_department_for_field_of_study import get_departments_for_field_of_study
from app.models.model_lessons import Lesson
from app.schemas.rapla.reservations.schema_rapla_apontment import SchemaRaplaApointment
from app.schemas.rapla.reservations.schema_rapla_reservation_zajencia import SchemaRaplaReservationZajencia
from app.schemas.rapla.schema_rapla_permision import RaplaPermission
from app.cruds.crud_lesson_for_group import	get_groups_for_lesson
from app.cruds.rapla.crud_rapla_group_to_resourc import get_resourc_by_group_id


def get_lessons(db: Session) -> list[Lesson]:
	return (
		db.query(Lesson)
		.order_by(Lesson.date.asc(), Lesson.start_time.asc(), Lesson.end_time.asc())
		.all()
	)


def get_lesson_by_id(db: Session, lesson_id: int) -> Optional[Lesson]:
	return db.query(Lesson).filter(Lesson.id == lesson_id).first()


def get_lesson_by_fields(
	db: Session,
	lesson_date: date,
	start_time: time,
	end_time: time,
	subject_id: int,
	room_id: int,
	user_id: int | None,
) -> Optional[Lesson]:
	query = db.query(Lesson).filter(
		Lesson.date == lesson_date,
		Lesson.start_time == start_time,
		Lesson.end_time == end_time,
		Lesson.subject_id == subject_id,
		Lesson.room_id == room_id,
	)
	if user_id is None:
		query = query.filter(Lesson.user_id.is_(None))
	else:
		query = query.filter(Lesson.user_id == user_id)

	return query.first()


def create_lesson(
	db: Session,
	*,
	lesson_date: date,
	start_time: time,
	end_time: time,
	subject_id: int,
	room_id: int,
	user_id: int | None = None,
) -> Lesson:
	lesson = Lesson(
		date=lesson_date,
		start_time=start_time,
		end_time=end_time,
		subject_id=subject_id,
		room_id=room_id,
		user_id=user_id,
	)
	db.add(lesson)
	db.commit()
	db.refresh(lesson)
	return lesson


def update_lesson(
	db: Session,
	lesson: Lesson,
	*,
	lesson_date: date | None = None,
	start_time: time | None = None,
	end_time: time | None = None,
	subject_id: int | None = None,
	room_id: int | None = None,
	user_id: int | None = None,
) -> Lesson:
	if lesson_date is not None:
		lesson.date = lesson_date
	if start_time is not None:
		lesson.start_time = start_time
	if end_time is not None:
		lesson.end_time = end_time
	if subject_id is not None:
		lesson.subject_id = subject_id
	if room_id is not None:
		lesson.room_id = room_id
	if user_id is not None:
		lesson.user_id = user_id

	db.add(lesson)
	db.commit()
	db.refresh(lesson)
	return lesson


def delete_lesson(db: Session, lesson_id: int) -> bool:
	lesson = get_lesson_by_id(db, lesson_id)
	if lesson is None:
		return False

	db.delete(lesson)
	db.commit()
	return True


def lessons_to_schema(db: Session) -> list[SchemaRaplaReservationZajencia]:
	lessons = get_lessons(db)
	owner = get_first_rapla_users_by_username(db, "system")
	owner_uuid = cast(str, owner.uuid) if owner is not None else ""

	now = datetime.now(timezone.utc)
	created_at = now.isoformat(timespec="milliseconds").replace("+00:00", "Z")
	last_changed = created_at

	reservations_by_key: dict[str, SchemaRaplaReservationZajencia] = {}
	for lesson in lessons:
		lesson_date = cast(date, lesson.date)
		start_time = cast(time, lesson.start_time).strftime("%H:%M:%S")
		end_time = cast(time, lesson.end_time).strftime("%H:%M:%S")
		groups = get_groups_for_lesson(db, lesson.id)

		allocate: list[str] = []
		for group in groups:
			group_resource = get_resourc_by_group_id(db, cast(int, group.id))
			if group_resource is not None and getattr(group_resource, "uuid", None):
				allocate.append(cast(str, group_resource.uuid))

		subject_resource = get_resourc_by_subject_id(db, cast(int, lesson.subject_id))
		if subject_resource is not None and getattr(subject_resource, "uuid", None):
			allocate.append(cast(str, subject_resource.uuid))

		room_resource = get_resorsc_by_room_id(db, cast(int, lesson.room_id))
		if room_resource is not None and getattr(room_resource, "uuid", None):
			allocate.append(cast(str, room_resource.uuid))

		if lesson.user_id is not None:
			user_resource = get_resorsc_by_user_id(db, cast(int, lesson.user_id))
			if user_resource is not None and getattr(user_resource, "uuid", None):
				allocate.append(cast(str, user_resource.uuid))

		allocate = list(dict.fromkeys(allocate))

		appointment = SchemaRaplaApointment(
			uuid=str(uuid4()),
			start_date=format_rapla_date(lesson_date),
			start_time=start_time,
			end_date=format_rapla_date(lesson_date),
			end_time=end_time,
			allocate=allocate,
		)

		name_value = "Zajencia"
		if subject_resource is not None and getattr(subject_resource, "uuid", None):
			name_value = cast(str, subject_resource.uuid)
		elif lesson.subject is not None:
			name_value = cast(str, lesson.subject.name)

		reservation = reservations_by_key.get(name_value)
		if reservation is None:
			# base permissions (read for others)
			permissions = [
				RaplaPermission(
					group="category[key='read-events-from-others']",
					access="read",
				)
			]


			field_of_study = None
			if getattr(lesson, "subject_id", None) is not None:
				field_of_study = get_primary_field_of_study_for_subject(db, cast(int, lesson.subject_id))



			if field_of_study is not None:
				departments = get_departments_for_field_of_study(db, cast(int, getattr(field_of_study, "id", None))) or []
				seen = set()
				for dept in departments:
					abbr = getattr(dept, "abbreviation", None)
					if not abbr:
						continue
					group = f"category[key='{abbr}_Editor']"
					if group in seen:
						continue
					seen.add(group)
					permissions.append(RaplaPermission(group=group, access="Edit"))
			

			reservation = SchemaRaplaReservationZajencia(
				uuid=str(uuid4()),
				owner=owner_uuid,
				created_at=created_at,
				last_changed=last_changed,
				last_changed_by=owner_uuid,
				appointments=[appointment],
				name=name_value,
				permissions=permissions,
			)
			reservations_by_key[name_value] = reservation
		else:
			reservation.appointments.append(appointment)

	return list(reservations_by_key.values())
