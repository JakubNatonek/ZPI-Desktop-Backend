from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.rapla.crud_rapla_categories import get_rapla_categories_schema
from app.cruds.rapla.crud_rapla_users import get_rapla_users_schema
from app.cruds.rapla.crud_rapla_define_element import get_define_element_full_schema
from app.schemas.rapla.schema_rapla_file import RaplaFile
from app.schemas.rapla.schema_rapla_grammar import RaplaGrammar
from app.schemas.rapla.schema_rapla_resources import SchemaRaplaResources
from app.cruds.rapla.crud_rapla_app_user_to_resourc import all_app_user_to_resourc_schema
from app.cruds.rapla.crud_rapla_room_to_resourc import all_room_to_resourc_schema
from app.cruds.rapla.crud_rapla_semester_to_resourc import all_semester_to_resourc_schema
from app.cruds.crud_dezyderata import dezyderaty_to_schema




router = APIRouter(prefix="/rapla", tags=["rapla"])


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
		resources_semester = all_semester_to_resourc_schema(db),
		resources_room = all_room_to_resourc_schema(db),
	)

	reservations = dezyderaty_to_schema(db)

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
		db: Session = Depends(get_db)
	):
	# Basic content-type check
	if file.content_type not in ("application/xml", "text/xml", "application/octet-stream"):
		raise HTTPException(status_code=400, detail="Expected an XML file")

	content = await file.read()
	try:
		xml_text = content.decode("utf-8")
	except Exception:
		raise HTTPException(status_code=400, detail="Unable to decode file as UTF-8")

	# Default summary in case import is not yet implemented
	summary = {}

	try:
		# r = parse_rapla_xml(xml_text)
		pass
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Failed to parse Rapla XML: {e}")

	
	try:
		# summary = import_rapla_file_to_db(db, r)
		pass
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to import Rapla data: {e}")

	return {"status": "ok", "summary": summary}
