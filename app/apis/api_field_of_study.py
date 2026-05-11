from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_field_of_study import get_field_of_studies
from app.dependencies.auth import require_role
from app.models.model_user import User


router = APIRouter(prefix="/field-of-studies", tags=["field-of-studies"])


class FieldOfStudyResponse(BaseModel):
    id: int
    name: str
    abbrevation: str
    year: int
    label: str


@router.get("/list", response_model=list[FieldOfStudyResponse])
def list_field_of_studies(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin", "rapla_editor"])),
) -> list[FieldOfStudyResponse]:
    items = get_field_of_studies(db)
    return [
        FieldOfStudyResponse(
            id=item.id,
            name=item.name,
            abbrevation=item.abbrevation,
            year=item.year,
            label=f"{item.name} / {item.abbrevation} / {item.year}",
        )
        for item in items
    ]