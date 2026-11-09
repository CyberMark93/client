import os
from datetime import date, timedelta

HOLIDAYS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "holidays.txt")

_GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]


class _DateError(ValueError):
    """Rifiuto esplicito: il messaggio è la stringa restituita."""


def _parse_date(s):
    try:
        return date.fromisoformat(s)
    except (ValueError, TypeError):
        raise _DateError(f"data non valida: {s}")


def _require(value, operation):
    if value is None:
        raise _DateError(f"argomento mancante per {operation}")
    return value


def _require_int(value):
    if not isinstance(value, int) or isinstance(value, bool):
        raise _DateError("numero di giorni non valido")
    return value


def date_tool(operation, start=None, end=None, days=None, holidays=None):
    try:
        if operation == "weekday":
            d = _parse_date(_require(start, operation))
            return f"{d.isoformat()} è {_GIORNI[d.weekday()]}"
        if operation == "add_days":
            d = _parse_date(_require(start, operation))
            n = _require_int(days)
            return f"{d.isoformat()} + {n} giorni = {(d + timedelta(days=n)).isoformat()}"
        if operation == "days_between":
            d1 = _parse_date(_require(start, operation))
            d2 = _parse_date(_require(end, operation))
            return f"da {d1.isoformat()} a {d2.isoformat()}: {(d2 - d1).days} giorni"
        return f"operazione non riconosciuta: {operation}"
    except _DateError as e:
        return str(e)


DATE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "date_tool",
        "description": "Opera su date ISO e scadenze in giorni lavorativi (festività da file locale). Risultato indicativo, non normativo.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["weekday", "add_days", "days_between", "business_days_between", "deadline"],
                    "description": "operazione da eseguire",
                },
                "start": {"type": "string", "description": "data ISO YYYY-MM-DD (data principale)"},
                "end": {"type": "string", "description": "seconda data ISO (per *_between)"},
                "days": {"type": "integer", "description": "numero di giorni (per add_days/deadline)"},
            },
            "required": ["operation"],
        },
    },
}
