from datetime import datetime, date

##
# @brief Format a datetime value to Rapla-compatible ISO 8601 string.
# @param value Datetime value or None.
# @return ISO string with Z suffix, or empty string when input is None.
def format_rapla_datetime(value: datetime | None) -> str:
	if value is None:
		return ""
	return value.isoformat().replace("+00:00", "Z")



def format_rapla_date(value: date) -> str:
	# Parse a `YYYY-MM-DD` string into a `date`.
	return value.isoformat()


def parse_rapla_date(value: str) -> date:
	# Parse a `YYYY-MM-DD` string into a `date`.
	return date.fromisoformat(value)


def parse_rapla_datetime(value: str | None) -> datetime | None:
	"""Parse a Rapla datetime string (ISO8601 with trailing Z) into a
	timezone-aware Python `datetime` in UTC.

	Returns None for empty/None input or when parsing fails.
	Examples:
		'2026-03-29T12:00:00Z' -> datetime(..., tzinfo=timezone.utc)
	"""
	if not value:
		return None

	s = value
	# Rapla uses trailing 'Z' for UTC; convert to a +00:00 offset for fromisoformat
	if s.endswith("Z"):
		s = s[:-1] + "+00:00"

	try:
		dt = datetime.fromisoformat(s)
		return dt
	except ValueError:
		return None

