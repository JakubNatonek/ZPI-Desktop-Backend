from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_role
from app.models.model_user import User
from app.models.model_group import Group
from pydantic import BaseModel

router = APIRouter(prefix="/groups", tags=["groups"])

class GroupResponse(BaseModel):
    id: int
    specialization: str
    code: str
    year: int
    studies_type: str

@router.get("/list", response_model=list[GroupResponse])
def get_groups(db: Session = Depends(get_db), _: User = Depends(require_role(["admin", "rapla_editor"]))):
    return db.query(Group).all()
