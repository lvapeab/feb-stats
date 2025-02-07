import datetime
import re
from typing import Any
from zoneinfo import ZoneInfo


def validate_string(value: str) -> str:
    clean_value: str = re.sub(r"\s+", " ", value.strip())
    return " ".join(clean_value.split())


def validate_int(value: Any) -> int:
    return int(value)


def validate_datetime(value: Any) -> datetime.datetime:
    if isinstance(value, datetime.datetime):
        return value.replace(tzinfo=ZoneInfo("Europe/Madrid"))
    if isinstance(value, str):
        date_str, time_str = value.split()
        return datetime.datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M").replace(
            tzinfo=ZoneInfo("Europe/Madrid")
        )

    raise ValueError(f"DateTime must be in 'dd/mm/yyyy HH:MM' format. Value: {value}")
