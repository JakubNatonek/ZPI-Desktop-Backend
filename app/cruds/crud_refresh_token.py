from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.model_refresh_token import RefreshTokenSession


def create_refresh_session(
    db: Session,
    *,
    user_id: int,
    jti: str,
    expires_at: datetime,
) -> RefreshTokenSession:
    session = RefreshTokenSession(user_id=user_id, jti=jti, expires_at=expires_at)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_refresh_session_by_jti(db: Session, jti: str) -> RefreshTokenSession | None:
    return db.query(RefreshTokenSession).filter(RefreshTokenSession.jti == jti).first()


def is_refresh_session_active(db: Session, jti: str) -> bool:
    session = get_refresh_session_by_jti(db, jti)
    if session is None:
        return False

    if session.revoked_at is not None:
        return False

    if session.expires_at <= datetime.now(timezone.utc):
        return False

    return True


def revoke_refresh_session(db: Session, jti: str) -> bool:
    session = get_refresh_session_by_jti(db, jti)
    if session is None:
        return False

    if session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
        db.add(session)
        db.commit()

    return True
