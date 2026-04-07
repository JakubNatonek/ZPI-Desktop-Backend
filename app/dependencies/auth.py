from fastapi import Depends, HTTPException, status

from app.auth.current_user import get_current_user
from app.models.model_user import User
from app.seed_data.seed_model.seed_roles import RolaEnum


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role is None or current_user.role.name != RolaEnum.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return current_user
