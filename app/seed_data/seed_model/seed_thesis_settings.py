from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.thesis_datetime import normalize_to_utc_minute
from app.cruds.crud_thesis_settings import get_or_create_thesis_settings


def seed_thesis_settings(db: Session) -> None:
    settings = get_or_create_thesis_settings(db)
    now = normalize_to_utc_minute(datetime.now(timezone.utc))
    if now is None:
        return
    changed = False

    if settings.tab_visible_from is None:
        settings.tab_visible_from = now - timedelta(days=14)
        changed = True
    if settings.tab_visible_to is None:
        settings.tab_visible_to = now + timedelta(days=120)
        changed = True
    if settings.topic_submission_from is None:
        settings.topic_submission_from = now - timedelta(days=7)
        changed = True
    if settings.topic_submission_to is None:
        settings.topic_submission_to = now + timedelta(days=45)
        changed = True
    if settings.proposal_selection_from is None:
        settings.proposal_selection_from = now - timedelta(days=2)
        changed = True
    if settings.proposal_selection_deadline is None:
        settings.proposal_selection_deadline = now + timedelta(days=60)
        changed = True
    if settings.max_approved_proposals is None or settings.max_approved_proposals < 1:
        settings.max_approved_proposals = 3
        changed = True

    if changed:
        db.add(settings)
        db.commit()
        db.refresh(settings)

    print("Thesis settings seeded.")
