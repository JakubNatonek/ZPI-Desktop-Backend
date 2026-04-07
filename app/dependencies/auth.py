from fastapi import Depends, HTTPException, status

from app.auth.current_user import get_current_user
from app.models.model_user import User


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    role_value = current_user.role.name if current_user.role else str(current_user.role)
    if role_value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return current_user
