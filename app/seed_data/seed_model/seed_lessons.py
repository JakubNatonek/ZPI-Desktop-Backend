import json
import unicodedata
from datetime import datetime, date, time
from typing import cast

from sqlalchemy.orm import Session

from app.cruds.crud_activity import get_all_activities, get_or_create_activity
from app.cruds.crud_lessons import create_lesson, get_lesson_by_fields
from app.cruds.crud_subject import create_subject, get_subject_by_name_and_activity
from app.cruds.room.crud_room import create_room
from app.cruds.room.crud_room_type import get_all_room_types, get_or_create_room_type
from app.models.model_activity import Activity
from app.models.model_room import Room
from app.models.model_subject import Subject
from app.models.model_user import User
from app.schemas.room import RoomCreate
from app.schemas.subject import SubjectCreate


TYPE_ACTIVITY_ALIASES: dict[str, str] = {
	"wyk": "wyklady",
	"sem": "seminaria",
	"proj": "projekty",
	"lab": "laboratoria",
	"cw": "cwiczenia",
}

TITLE_TOKENS = {
	"mgr",
	"inz",
	"dr",
	"hab",
	"prof",
	"profesor",
}


def _normalize_text(value: str) -> str:
	if not value:
		return ""

	normalized = unicodedata.normalize("NFKD", value)
	stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
	return "".join(ch for ch in stripped.lower() if ch.isalnum())


def _parse_date(value: str | None) -> date | None:
	if not value:
		return None

	try:
		return datetime.strptime(value.strip(), "%Y.%m.%d").date()
	except ValueError:
		return None


def _parse_time(value: str | None) -> time | None:
	if not value:
		return None

	try:
		return datetime.strptime(value.strip(), "%H:%M").time()
	except ValueError:
		return None


def _extract_room_number(raw: str | None) -> str | None:
	if not raw:
		return None

	parts = [part for part in raw.split() if part]
	if not parts:
		return None

	return parts[-1].strip()


def _build_room_lookup(db: Session) -> dict[str, Room]:
	lookup: dict[str, Room] = {}
	for room in db.query(Room).all():
		number = (room.number or "").strip()
		if not number:
			continue

		key = number.lower()
		if key not in lookup:
			lookup[key] = room

		first_token = number.split()[0].lower()
		if first_token not in lookup:
			lookup[first_token] = room

	return lookup


def _build_user_lookup(db: Session) -> dict[tuple[str, str], User]:
	lookup: dict[tuple[str, str], User] = {}
	for user in db.query(User).all():
		key = (
			_normalize_text(cast(str, user.first_name)),
			_normalize_text(cast(str, user.last_name)),
		)
		if key not in lookup:
			lookup[key] = user
	return lookup


def _extract_teacher_key(raw: str | None) -> tuple[str, str] | None:
	if not raw:
		return None

	tokens = [token for token in raw.replace(",", " ").split() if token]
	name_tokens: list[str] = []
	for token in tokens:
		normalized = _normalize_text(token)
		if not normalized or normalized in TITLE_TOKENS:
			continue
		name_tokens.append(token)

	if len(name_tokens) < 2:
		return None

	first = _normalize_text(name_tokens[0])
	last = _normalize_text(name_tokens[-1])
	if not first or not last:
		return None

	return (first, last)


def _build_activity_lookup(db: Session) -> dict[str, Activity]:
	lookup: dict[str, Activity] = {}
	for activity in get_all_activities(db):
		key = _normalize_text(cast(str, activity.name))
		if key and key not in lookup:
			lookup[key] = activity
	return lookup


def _resolve_activity(
	db: Session,
	activity_lookup: dict[str, Activity],
	lesson_type: str | None,
) -> Activity | None:
	raw_key = _normalize_text(lesson_type or "")
	if not raw_key:
		return None

	activity_name = TYPE_ACTIVITY_ALIASES.get(raw_key, raw_key)
	normalized = _normalize_text(activity_name)
	activity = activity_lookup.get(normalized)
	if activity is None:
		activity = get_or_create_activity(db, activity_name)
		activity_lookup[_normalize_text(cast(str, activity.name))] = activity

	return activity


def _resolve_default_room_type_id(db: Session) -> int | None:
	room_types = get_all_room_types(db)
	if room_types:
		return cast(int, room_types[0].id)

	created = get_or_create_room_type(db, "Default", "DF")
	return cast(int, created.id)


def _ensure_room(
	db: Session,
	room_lookup: dict[str, Room],
	room_number: str,
	default_room_type_id: int | None,
) -> Room | None:
	key = room_number.lower()
	room = room_lookup.get(key)
	if room is not None:
		return room

	if default_room_type_id is None:
		return None

	try:
		payload = RoomCreate.model_validate(
			{
				"room_number": room_number,
				"seats_count": 1,
				"room_type_id": default_room_type_id,
				"special_equipment": [],
				"activities": [],
				"departments": [],
			}
		)
		room = create_room(
			db,
			payload,
		)
	except Exception:
		return None

	room_lookup[key] = room
	first_token = room_number.split()[0].lower()
	room_lookup.setdefault(first_token, room)
	return room


def _resolve_subject(
	db: Session,
	subject_cache: dict[tuple[str, int], Subject],
	subject_name: str,
	activity_id: int,
	type_display: str | None,
	) -> Subject:
	key = (subject_name.strip().lower(), activity_id)
	cached = subject_cache.get(key)
	if cached is not None:
		return cached

	subject = get_subject_by_name_and_activity(db, subject_name, activity_id)
	if subject is None:
		subject = create_subject(
			db,
			SubjectCreate(
				name=subject_name,
				activity_id=activity_id,
				type_display=type_display,
				room_properties=None,
				blocked=False,
				periodic=False,
			),
		)

	subject_cache[key] = subject
	return subject


def seed_lessons(db: Session, path: str = "data/JSON DATA/lessons.json") -> None:
	with open(path, "r", encoding="utf-8") as fh:
		data = json.load(fh)

	activity_lookup = _build_activity_lookup(db)
	room_lookup = _build_room_lookup(db)
	user_lookup = _build_user_lookup(db)
	default_room_type_id = _resolve_default_room_type_id(db)
	subject_cache: dict[tuple[str, int], Subject] = {}

	created_count = 0
	skipped_count = 0
	for entry in data:
		lesson_date = _parse_date(entry.get("date"))
		start_time = _parse_time(entry.get("from"))
		end_time = _parse_time(entry.get("to"))
		if lesson_date is None or start_time is None or end_time is None:
			skipped_count += 1
			continue

		room_number = _extract_room_number(entry.get("room"))
		if not room_number:
			skipped_count += 1
			continue

		room = _ensure_room(db, room_lookup, room_number, default_room_type_id)
		if room is None:
			skipped_count += 1
			continue

		activity = _resolve_activity(db, activity_lookup, entry.get("type"))
		if activity is None:
			skipped_count += 1
			continue

		subject_name = (entry.get("subject") or "").strip()
		if not subject_name:
			skipped_count += 1
			continue

		subject = _resolve_subject(
			db,
			subject_cache,
			subject_name,
			cast(int, activity.id),
			entry.get("type"),
		)

		user_id = None
		teacher_key = _extract_teacher_key(entry.get("teacher"))
		if teacher_key is not None:
			user = user_lookup.get(teacher_key)
			if user is not None:
				user_id = cast(int, user.user_id)

		existing = get_lesson_by_fields(
			db,
			lesson_date,
			start_time,
			end_time,
			cast(int, subject.id),
			cast(int, room.id),
			user_id,
		)
		if existing is not None:
			continue

		create_lesson(
			db,
			lesson_date=lesson_date,
			start_time=start_time,
			end_time=end_time,
			subject_id=cast(int, subject.id),
			room_id=cast(int, room.id),
			user_id=user_id,
		)
		created_count += 1

	print(f"Lessons seeded. Added: {created_count}, skipped: {skipped_count}")
