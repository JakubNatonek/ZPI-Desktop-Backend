from collections.abc import Iterable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.crud_role import get_roles
from app.models.model_user import User

def require_role(required_role: str | Iterable[str] | None = None):
    required_roles: set[str] | None
    if required_role is None:
        required_roles = None
    elif isinstance(required_role, str):
        required_roles = {required_role.strip().lower()} if required_role.strip() else set()
    else:
        required_roles = {
            str(role).strip().lower()
            for role in required_role
            if str(role).strip()
        }

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

        if required_roles is not None and matched_roles.isdisjoint(required_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        return current_user

    return dependency
