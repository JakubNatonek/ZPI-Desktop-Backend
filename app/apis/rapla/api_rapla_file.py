from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.rapla.crud_rapla_categories import get_rapla_categories_schema
from app.cruds.rapla.crud_rapla_users import get_rapla_users_schema
from app.cruds.rapla.crud_rapla_define_element import get_define_element_full_schema
from app.schemas.rapla.schema_rapla_file import RaplaFile
from app.schemas.rapla.schema_rapla_grammar import RaplaGrammar


router = APIRouter(prefix="/rapla", tags=["rapla"])


@router.get("/file", summary="Generate and download Rapla XML")
def generate_rapla_file(db: Session = Depends(get_db)) -> FileResponse:
	output_path = Path(__file__).resolve().parents[3] / "data" / "rapla_files" / "data.xml"
	output_path.parent.mkdir(parents=True, exist_ok=True)


	users = get_rapla_users_schema(db)
	categories = get_rapla_categories_schema(db)
	grammar = RaplaGrammar( get_define_element_full_schema(db) )
	data = RaplaFile(users=users, categories=categories, grammar=grammar)
	data.save_to_file(str(output_path))

	return FileResponse(
		path=output_path,
		media_type="application/xml",
		filename="data.xml",
	)
