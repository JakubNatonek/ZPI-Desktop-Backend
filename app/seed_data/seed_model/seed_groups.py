import json
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.cruds.crud_field_of_study import (
	get_field_of_study_by_abbrevation,
	get_field_of_study_by_abbrevation_and_year,
)
from app.cruds.crud_field_of_study_for_group import (
	create_field_of_study_for_group_maping,
	get_groups_from_maping_by_field_of_study_id,
)
from app.cruds.crud_group import create_group, ensure_resourc
from app.models.model_field_of_study import FieldOfStudy


def _resolve_data_path(path: str) -> Path:
	file_path = Path(path)
	if file_path.is_absolute():
		return file_path
	return (Path(__file__).resolve().parents[2] / file_path).resolve()


def _load_json(path: str) -> list[dict[str, object]]:
	with open(_resolve_data_path(path), "r", encoding="utf-8") as fh:
		return json.load(fh)


def _find_field_of_study(db: Session, abbrev: str | None, year: Optional[int]) -> FieldOfStudy | None:
	if not abbrev:
		return None

	if year is not None:
		try:
			field_of_study = get_field_of_study_by_abbrevation_and_year(db, abbrev, year)
			if field_of_study is not None:
				return field_of_study
		except Exception:
			pass

	try:
		return get_field_of_study_by_abbrevation(db, abbrev)
	except Exception:
		return None


def seed_groups(db: Session, path: str = "data/JSON DATA/grupy.json") -> None:
	try:
		data = _load_json(path)
	except FileNotFoundError:
		print("No group seed file found; skipping groups seeding")
		return
	except Exception as exc:
		print(f"Unable to load group seed file: {exc}")
		return

	created = 0
	mapped = 0

	for entry in data:
		if not isinstance(entry, dict):
			continue

		code = entry.get("kod") or entry.get("a1")
		spec = entry.get("spec")
		rok = entry.get("rok")

		if code is None:
			if spec and rok:
				code = f"{spec}{rok}"
			elif spec:
				code = spec
			else:
				continue

		code = str(code).strip()
		if not code:
			continue

		year: int | None = None
		if isinstance(rok, int):
			year = rok
		elif isinstance(rok, str):
			try:
				year = int(rok)
			except ValueError:
				year = None

		abbrev = str(spec).strip() if spec is not None else None
		field_of_study = _find_field_of_study(db, abbrev, year)
		if field_of_study is None:
			continue

		groups = get_groups_from_maping_by_field_of_study_id(db, field_of_study.id)
		if any(exist.code == code for exist in groups):
			mapped += 1
			continue

		group = create_group(db, code=code)
		create_field_of_study_for_group_maping(
			db,
			id_field_of_study=field_of_study.id,
			id_group=group.id,
		)
		ensure_resourc(db, group)
		created += 1

	print(f"Groups seeded. Created: {created}, Field mappings added: {mapped}")
