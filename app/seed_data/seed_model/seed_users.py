import json
import random
import unicodedata
from pathlib import Path
from typing import Optional, cast

from sqlalchemy.orm import Session

from app.cruds.crud_department import get_department_by_abbreviation
from app.cruds.crud_role import get_role_by_name
from app.cruds.crud_title import create_title, get_title_by_name
from app.cruds.crud_user import create_user_by_admin, get_user_by_login
from app.seed_data.seed_model.seed_titles import TytulEnum


def _resolve_data_path(path: str) -> Path:
	file_path = Path(path)
	if file_path.is_absolute():
		return file_path
	return (Path(__file__).resolve().parents[2] / file_path).resolve()


def _load_json(path: str) -> list[dict[str, object]]:
	with open(_resolve_data_path(path), "r", encoding="utf-8") as fh:
		return json.load(fh)


def _strip_diacritics(s: str) -> str:
	nk = unicodedata.normalize("NFKD", s)
	return "".join(c for c in nk if not unicodedata.combining(c) and c.isalpha())


def _make_login(first: str, last: str, db: Session, max_attempts: int = 20) -> Optional[str]:
	f = _strip_diacritics(first).lower()
	l = _strip_diacritics(last).lower()
	f3 = (f + "xxx")[:3]
	l3 = (l + "xxx")[:3]

	for _ in range(max_attempts):
		digits = "".join(random.choices("0123456789", k=5))
		login = f"{f3}{digits}{l3}"
		if get_user_by_login(db, login) is None:
			return login

	return None


def seed_users(db: Session, path: str = "data/JSON DATA/nauczyciele.json") -> None:
	try:
		data = _load_json(path)
	except FileNotFoundError:
		print("No user seed file found; skipping users seeding")
		return
	except Exception as exc:
		print(f"Unable to load user seed file: {exc}")
		return

	default_password = "test123"
	role = get_role_by_name(db=db, name="wykladowca")
	if role is None:
		print("Role 'wykladowca' not found; skipping users seeding")
		return

	dept = get_department_by_abbreviation(db=db, abbreviation="WI")
	if dept is None:
		print("Department 'WI' not found; skipping users seeding")
		return

	created = 0
	for entry in data:
		if not isinstance(entry, dict):
			continue

		last = str(entry.get("nazwisko") or "").strip()
		first = str(entry.get("imie") or "").strip()
		t_code = entry.get("tytul")

		if not first or not last:
			continue

		title_row = None
		if isinstance(t_code, str) and t_code:
			try:
				title_value = TytulEnum[t_code].value
			except Exception:
				title_value = None
			if title_value:
				title_row = get_title_by_name(db, title_value)
				if title_row is None:
					title_row = create_title(db, title_value)

		title_ids = [cast(int, title_row.id)] if title_row is not None else None
		login = _make_login(first, last, db)
		if login is None:
			print(f"Could not generate login for {first} {last}; skipping user")
			continue

		try:
			create_user_by_admin(
				db=db,
				first_name=first,
				last_name=last,
				role_ids=[cast(int, role.id)],
				department_ids=[cast(int, dept.id)],
				password=default_password,
				login=login,
				title_ids=title_ids,
				admin=None,
			)
			created += 1
		except Exception as exc:
			print(f"Error creating user {first} {last}: {exc}")

	print(f"Users seeded. Created: {created}")
