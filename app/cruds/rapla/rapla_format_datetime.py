from datetime import datetime

##
# @brief Format a datetime value to Rapla-compatible ISO 8601 string.
# @param value Datetime value or None.
# @return ISO string with Z suffix, or empty string when input is None.
def format_rapla_datetime(value: datetime | None) -> str:
	if value is None:
		return ""
	return value.isoformat().replace("+00:00", "Z")

