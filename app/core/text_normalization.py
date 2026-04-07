import unicodedata


POLISH_CHAR_TRANSLATION = str.maketrans({
    "ą": "a",
    "ć": "c",
    "ę": "e",
    "ł": "l",
    "ń": "n",
    "ó": "o",
    "ś": "s",
    "ź": "z",
    "ż": "z",
    "Ą": "A",
    "Ć": "C",
    "Ę": "E",
    "Ł": "L",
    "Ń": "N",
    "Ó": "O",
    "Ś": "S",
    "Ź": "Z",
    "Ż": "Z",
})

# NOTE: WHERE IS THIS USED AND WHY??
def normalize_lookup_value(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", (value or "").translate(POLISH_CHAR_TRANSLATION))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_value.strip().lower()