from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.rapla.crud_rapla_categories import get_rapla_categories_schema
from app.cruds.rapla.crud_rapla_users import get_rapla_users_schema
from app.cruds.rapla.crud_rapla_define_element import get_define_element_full_schema
from app.cruds.rapla.crud_rapla_imported_reservation import upsert_rapla_reservations
from app.models.model_user import User
from app.models.rapla.model_rapla_imported_reservation import RaplaImportedReservation
from app.schemas.rapla.schema_rapla_file import RaplaFile
from app.schemas.rapla.schema_rapla_grammar import RaplaGrammar
from app.schemas.rapla.schema_rapla_resources import SchemaRaplaResources
from app.cruds.rapla.crud_rapla_app_user_to_resourc import all_app_user_to_resourc_schema
from app.cruds.rapla.crud_rapla_room_to_resourc import all_room_to_resourc_schema
from app.cruds.rapla.crud_rapla_subject_to_resourc import all_subject_to_resourc_schema
from app.services.rapla_xml_parser import parse_rapla_reservations
from app.cruds.rapla.crud_rapla_semester_to_resourc import all_semester_to_resourc_schema
from app.cruds.crud_dezyderata import dezyderaty_to_schema
from app.cruds.crud_lessons import lessons_to_schema
from app.cruds.crud_teaching_load import teaching_load_assignments_to_schema
from app.cruds.rapla.crud_rapla_group_to_resourc import all_group_to_resourc_schema


router = APIRouter(prefix="/rapla", tags=["rapla"])


class RaplaReservationDto(BaseModel):
	id: int
	uuid: str
	name: Optional[str]
	color: Optional[str]
	reservation_type: Optional[str]
	reservation_uuid: Optional[str]
	activity_type: Optional[str]
	start_date: Optional[str]
	start_time: Optional[str]
	end_date: Optional[str]
	end_time: Optional[str]
	repeating_type: Optional[str]
	repeating_end_date: Optional[str]
	allocate: Optional[list[str]]
	room_names: Optional[list[str]]
	teacher_names: Optional[list[str]]
	semester_names: Optional[list[str]]
	group_names: Optional[list[str]]

	model_config = {"from_attributes": True}


@router.get(
        "/reservations",
        response_model=list[RaplaReservationDto],
        summary="Get all imported Rapla reservations"
    )
def get_rapla_reservations(
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> list[RaplaImportedReservation]:
    return db.query(RaplaImportedReservation).order_by(RaplaImportedReservation.start_date.asc()).all()


@router.get(
		"/file", 
		summary="Generate and download Rapla XML"
	)
def generate_rapla_file(
		db: Session = Depends(get_db)
	) -> FileResponse:
	
	output_path = Path(__file__).resolve().parents[3] / "data" / "rapla_files" / "data.xml"
	output_path.parent.mkdir(parents=True, exist_ok=True)


	users = get_rapla_users_schema(db)
	categories = get_rapla_categories_schema(db)
	grammar = RaplaGrammar( get_define_element_full_schema(db) )
	resources = SchemaRaplaResources( 
		resources_nauczyciel = all_app_user_to_resourc_schema(db),
		resources_przedmiot = all_subject_to_resourc_schema(db),
		resources_semester = all_semester_to_resourc_schema(db),
		resources_room = all_room_to_resourc_schema(db),
		resources_grupa = all_group_to_resourc_schema(db),
	)

	reservations = dezyderaty_to_schema(db)
	reservations.zajencia = lessons_to_schema(db)
	reservations.zajencia.extend(teaching_load_assignments_to_schema(db))

	data = RaplaFile(users=users, categories=categories, grammar=grammar, resources=resources, reservations=reservations)
	data.save_to_file(str(output_path))

	return FileResponse(
		path=output_path,
		media_type="application/xml",
		filename="data.xml",
	)


@router.post(
		"/file/import",
		summary="Import Rapla XML file into DB"
	)
async def import_rapla_file(
		file: UploadFile = File(...),
		db: Session = Depends(get_db),
		current_user: User = Depends(get_current_user),
	):
	# Basic content-type check
	if file.content_type not in ("application/xml", "text/xml", "application/octet-stream"):
		raise HTTPException(status_code=400, detail="Expected an XML file")

	content = await file.read()
	try:
		xml_text = content.decode("utf-8")
	except Exception:
		raise HTTPException(status_code=400, detail="Unable to decode file as UTF-8")

	try:
		reservations = parse_rapla_reservations(xml_text)
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Failed to parse Rapla XML: {e}")

	modified_by_name = f"{current_user.first_name} {current_user.last_name}".strip() or str(current_user.user_id)

	try:
		summary = upsert_rapla_reservations(
			db=db,
			reservations=reservations,
			modified_by=current_user.user_id,
			modified_by_name=modified_by_name,
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to import Rapla data: {e}")

	return {"status": "ok", "summary": summary}
