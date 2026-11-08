from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from convert import convert_units, CONVERT_TOOL_SCHEMA


def get_current_time(timezone, now=None):
    try:
        tz = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        return f"Fuso orario non valido: {timezone}"
    if now is None:
        current = datetime.now(tz)
    elif now.tzinfo is None:
        current = now.replace(tzinfo=tz)
    else:
        current = now.astimezone(tz)
    return f"{current.isoformat(timespec='seconds')} ({timezone})"


CLOCK_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Restituisce l'ora corrente per un fuso orario IANA.",
        "parameters": {
            "type": "object",
            "properties": {"timezone": {"type": "string", "description": "es. Europe/Rome"}},
            "required": ["timezone"],
        },
    },
}
CLOCK_TOOLS = [CLOCK_TOOL_SCHEMA]
TOOLS = [CLOCK_TOOL_SCHEMA, CONVERT_TOOL_SCHEMA]
TOOL_REGISTRY = {
    "get_current_time": get_current_time,
    "convert_units": convert_units,
}
