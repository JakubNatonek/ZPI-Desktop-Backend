from collections.abc import Iterable

from fastapi import Depends, HTTPException, status

from app.auth.current_user import get_current_user, get_user_role_names
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
    ) -> User:
        user_roles = get_user_role_names(current_user)
        if not user_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        if required_roles is not None and user_roles.isdisjoint(required_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        return current_user

    return dependency
