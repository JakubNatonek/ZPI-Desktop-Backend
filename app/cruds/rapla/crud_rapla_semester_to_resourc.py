from sqlalchemy.orm import Session
from typing import cast

from datetime import datetime, date

from app.models.rapla.model_rapla_semester_to_resourc import RaplaSemesterToResourc
from app.models.rapla.model_rapla_resourc import ModelRaplaResourc

# For building Rapla schema objects
from app.models.model_semestr import Semestr
from app.schemas.rapla.resorces.schema_rapla_resourc_semester import SchemaRaplaResourcSemester
from app.cruds.rapla.crud_rapla_permission_for_resourc import get_permission_by_resourc_id
from app.cruds.rapla.crud_rapla_permission import get_permission_schema_by_model
from app.cruds.rapla.rapla_format_datetime import format_rapla_datetime, format_rapla_date
from app.schemas.rapla.schema_rapla_permision import RaplaPermission


def list_semester_to_resourc_mappings(db: Session) -> list[RaplaSemesterToResourc]:
	return db.query(RaplaSemesterToResourc).order_by(RaplaSemesterToResourc.id.asc()).all()


def get_resorsc_by_semestr_id(db: Session, semestr_id: int) -> ModelRaplaResourc | None:
	mapping = (
		db.query(RaplaSemesterToResourc)
		.filter(RaplaSemesterToResourc.semester_id == semestr_id)
		.first()
	)
	if mapping is None:
		return None

	return db.query(ModelRaplaResourc).filter(ModelRaplaResourc.id == mapping.rapla_resourc_id).first()


def get_mapping_by_semestr_and_resourc(db: Session, semestr_id: int, rapla_resourc_id: int) -> RaplaSemesterToResourc | None:
	return (
		db.query(RaplaSemesterToResourc)
		.filter(RaplaSemesterToResourc.semester_id == semestr_id)
		.filter(RaplaSemesterToResourc.rapla_resourc_id == rapla_resourc_id)
		.first()
	)


def create_semester_to_resourc_mapping(db: Session, semestr_id: int, rapla_resourc_id: int) -> RaplaSemesterToResourc:
	existing = get_mapping_by_semestr_and_resourc(db, semestr_id, rapla_resourc_id)
	if existing is not None:
		return existing

	m = RaplaSemesterToResourc(semester_id=semestr_id, rapla_resourc_id=rapla_resourc_id)
	db.add(m)
	db.commit()
	db.refresh(m)
	return m


def delete_semester_to_resourc_mapping(db: Session, semestr_id: int, rapla_resourc_id: int) -> bool:
	mapping = get_mapping_by_semestr_and_resourc(db, semestr_id, rapla_resourc_id)
	if mapping is None:
		return False
	db.delete(mapping)
	db.commit()
	return True


def semester_to_resourc_schema(db: Session, semestr: Semestr) -> SchemaRaplaResourcSemester | None:
	"""Convert a Semestr model (with mapped Rapla resource) to SchemaRaplaResourcSemester."""
	# find resource mapped to this semester
	res = get_resorsc_by_semestr_id(db, cast(int, semestr.id))
	if res is None:
		return None

	# gather permissions
	perm_models = get_permission_by_resourc_id(db, cast(int, res.id))
	perm_schemas: list[RaplaPermission] = []
	for p in perm_models:
		try:
			ps = get_permission_schema_by_model(db, p)
			if ps is not None:
				perm_schemas.append(ps)
		except Exception:
			continue

	# dates as YYYY-MM-DD
	start = format_rapla_date( cast(date, semestr.data_rozpoczecia) )
	end = format_rapla_date( cast(date, semestr.data_zakonczenia) )

	return SchemaRaplaResourcSemester(
		uuid=cast(str, res.uuid),
		owner=cast(str, res.owner),
		created_at=format_rapla_datetime(cast(datetime, res.created_at)),
		last_changed=format_rapla_datetime(cast(datetime, res.last_changed)),
		last_changed_by=cast(str, res.last_changed_by),
		name=cast(str, semestr.nazwa ) or "",
		start=start,
		end=end,
		permissions=perm_schemas,
	)


def all_semester_to_resourc_schema(db: Session) -> list[SchemaRaplaResourcSemester]:
	"""Return list of SchemaRaplaResourcSemester for all semesters that have a Rapla resource mapping."""
	semestrs = db.query(Semestr).order_by(Semestr.data_rozpoczecia.asc()).all()
	schemas: list[SchemaRaplaResourcSemester] = []
	for sem in semestrs:
		try:
			s = semester_to_resourc_schema(db, sem)
			if s is not None:
				schemas.append(s)
		except Exception:
			# skip problematic entries
			continue
	return schemas