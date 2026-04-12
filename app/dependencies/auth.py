from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.crud_role import get_roles
from app.models.model_user import User

def require_role(required_role: str | None = None):
    normalized_required_role = required_role.strip().lower() if required_role else None

    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        token_roles = {
            str(role).strip().lower()
            for role in getattr(current_user, "token_roles", [])
            if str(role).strip()
        }
        if not token_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        available_roles = {
            str(role.name).strip().lower()
            for role in get_roles(db)
            if role.name
        }
        matched_roles = token_roles.intersection(available_roles)
        if not matched_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        if normalized_required_role is not None and normalized_required_role not in matched_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        return current_user

    return dependency
