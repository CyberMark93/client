import csv
import json
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


def _parse_holiday(token, source):
    try:
        return date.fromisoformat(token)
    except (ValueError, TypeError):
        raise _DateError(f"festività non valida in {source}: {token}")


def _load_txt(path):
    result = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            result.add(_parse_holiday(line.split()[0], path))
    return result


def _load_csv(path):
    result = set()
    with open(path, encoding="utf-8", newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if not row or not row[0].strip():
                continue
            cell = row[0].strip()
            try:
                result.add(date.fromisoformat(cell))
            except ValueError:
                if i == 0:
                    continue  # intestazione
                raise _DateError(f"festività non valida in {path}: {cell}")
    return result


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    result = set()
    for item in data:
        token = item["date"] if isinstance(item, dict) else item
        result.add(_parse_holiday(token, path))
    return result


def load_holidays(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        return _load_txt(path)
    if ext == ".csv":
        return _load_csv(path)
    if ext == ".json":
        return _load_json(path)
    raise _DateError(f"formato festività non supportato: {ext}")


def _require(value, operation):
    if value is None:
        raise _DateError(f"argomento mancante per {operation}")
    return value


def _require_int(value):
    if not isinstance(value, int) or isinstance(value, bool):
        raise _DateError("numero di giorni non valido")
    return value


def _is_business_day(d, holidays):
    return d.weekday() < 5 and d not in holidays


def business_days_between(start, end, holidays):
    if end < start:
        raise _DateError("intervallo invertito")
    count = 0
    cur = start
    while cur < end:
        if _is_business_day(cur, holidays):
            count += 1
        cur += timedelta(days=1)
    return count


def deadline(start, days, holidays):
    if days <= 0:
        raise _DateError("i giorni devono essere positivi")
    cur = start
    n = 0
    while n < days:
        cur += timedelta(days=1)
        if _is_business_day(cur, holidays):
            n += 1
    return cur


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
        if operation == "business_days_between":
            d1 = _parse_date(_require(start, operation))
            d2 = _parse_date(_require(end, operation))
            hol = holidays if holidays is not None else load_holidays(HOLIDAYS_PATH)
            n = business_days_between(d1, d2, hol)
            return f"da {d1.isoformat()} a {d2.isoformat()}: {n} giorni lavorativi"
        if operation == "deadline":
            d = _parse_date(_require(start, operation))
            n = _require_int(days)
            hol = holidays if holidays is not None else load_holidays(HOLIDAYS_PATH)
            r = deadline(d, n, hol)
            return f"scadenza: {n} giorni lavorativi dopo {d.isoformat()} = {r.isoformat()}"
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
