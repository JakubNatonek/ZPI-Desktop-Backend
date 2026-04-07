from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.model_thesis_settings import ThesisScheduleSettings


SETTINGS_ROW_ID = 1


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def get_or_create_thesis_settings(db: Session) -> ThesisScheduleSettings:
    settings = db.query(ThesisScheduleSettings).filter(ThesisScheduleSettings.id == SETTINGS_ROW_ID).first()
    if settings is not None:
        return settings

    settings = ThesisScheduleSettings(id=SETTINGS_ROW_ID)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def update_thesis_settings(
    db: Session,
    *,
    tab_visible_from: datetime | None,
    tab_visible_to: datetime | None,
    topic_submission_from: datetime | None,
    topic_submission_to: datetime | None,
    proposal_selection_from: datetime | None,
    proposal_selection_deadline: datetime | None,
) -> ThesisScheduleSettings:
    settings = get_or_create_thesis_settings(db)
    settings.tab_visible_from = _normalize_datetime(tab_visible_from)
    settings.tab_visible_to = _normalize_datetime(tab_visible_to)
    settings.topic_submission_from = _normalize_datetime(topic_submission_from)
    settings.topic_submission_to = _normalize_datetime(topic_submission_to)
    settings.proposal_selection_from = _normalize_datetime(proposal_selection_from)
    settings.proposal_selection_deadline = _normalize_datetime(proposal_selection_deadline)

    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def _is_in_window(now: datetime, start: datetime | None, end: datetime | None) -> bool:
    normalized_start = _normalize_datetime(start)
    normalized_end = _normalize_datetime(end)

    if normalized_start is not None and now < normalized_start:
        return False
    if normalized_end is not None and now > normalized_end:
        return False
    return True


def get_thesis_schedule_flags(
    settings: ThesisScheduleSettings,
    *,
    now: datetime | None = None,
) -> dict[str, bool]:
    current_time = _normalize_datetime(now) or datetime.now(timezone.utc)
    return {
        "tab_visible_now": _is_in_window(current_time, settings.tab_visible_from, settings.tab_visible_to),
        "topic_submission_open": _is_in_window(
            current_time,
            settings.topic_submission_from,
            settings.topic_submission_to,
        ),
        "proposal_selection_open": _is_in_window(
            current_time,
            settings.proposal_selection_from,
            settings.proposal_selection_deadline,
        ),
    }