from datetime import datetime, timezone

THESIS_DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def parse_datetime_minute(value: str) -> datetime:
    parsed = datetime.strptime(value.strip(), THESIS_DATETIME_FORMAT)
    return parsed.replace(tzinfo=timezone.utc)


def normalize_to_utc_minute(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        normalized = value.replace(tzinfo=timezone.utc)
    else:
        normalized = value.astimezone(timezone.utc)
    formatted = normalized.strftime(THESIS_DATETIME_FORMAT)
    return parse_datetime_minute(formatted)


def utc_now_minute() -> datetime:
    now = datetime.now(timezone.utc)
    formatted = now.strftime(THESIS_DATETIME_FORMAT)
    return parse_datetime_minute(formatted)


def format_datetime_minute(value: datetime | None) -> str | None:
    normalized = normalize_to_utc_minute(value)
    if normalized is None:
        return None
    return normalized.strftime(THESIS_DATETIME_FORMAT)
