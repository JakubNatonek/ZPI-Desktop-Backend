import json
from typing import Optional

from sqlalchemy.orm import Session

from app.cruds.crud_group import create_group, ensure_resourc
from app.cruds.crud_field_of_study_for_group import create_field_of_study_for_group_maping
from app.cruds.crud_field_of_study import (
	get_field_of_study_by_abbrevation,
	get_field_of_study_by_abbrevation_and_year,
)
from app.models.model_field_of_study import FieldOfStudy
from app.models.model_group import Group


def _find_field_of_study(db: Session, abbrev: str | None, year: Optional[int]) -> FieldOfStudy | None:
	if not abbrev:
		return None

	# Prefer exact abbreviation+year match when year is provided
	if year is not None:
		try:
			f = get_field_of_study_by_abbrevation_and_year(db, abbrev, year)
			if f is not None:
				return f
		except Exception:
			pass

	# Fallback to abbreviation-only lookup
	try:
		return get_field_of_study_by_abbrevation(db, abbrev)
	except Exception:
		return None


def seed_groups(db: Session, path: str = "data/JSON DATA/grupy.json") -> None:
	from app.cruds.crud_field_of_study_for_group import get_groups_from_maping_by_field_of_study_id

	try:
		with open(path, "r", encoding="utf-8") as fh:
			data = json.load(fh)
	except Exception:
		print("No group seed file found; skipping groups seeding")
		return

	created = 0
	mapped = 0
	for entry in data:
		# prefer explicit 'kod' or 'a1' as group code; fallback to spec+rok
		code = entry.get("kod") or entry.get("a1") or None
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
		group = None
		field_of_study = get_field_of_study_by_abbrevation_and_year(db, spec, rok)
		if field_of_study is not None:
			groups = get_groups_from_maping_by_field_of_study_id(db, field_of_study.id)
			for exist in groups:
				if exist.code == code:
					mapped += 1
					break
			else:
				group = create_group(db, code=code)
				create_field_of_study_for_group_maping(db, id_field_of_study=field_of_study.id, id_group=group.id)
				ensure_resourc(db, group)
				created += 1

	print(f"Groups seeded. Created: {created}, Field mappings added: {mapped}")