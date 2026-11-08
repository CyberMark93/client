import math

# Unità a rapporto: simbolo -> (categoria, fattore verso l'unità-base della categoria)
_RATIO_UNITS = {
    # lunghezza (base: m)
    "m": ("lunghezza", 1.0),
    "km": ("lunghezza", 1000.0),
    "cm": ("lunghezza", 0.01),
    "mm": ("lunghezza", 0.001),
    "mi": ("lunghezza", 1609.344),
    "ft": ("lunghezza", 0.3048),
    "in": ("lunghezza", 0.0254),
    "yd": ("lunghezza", 0.9144),
    # peso/massa (base: kg)
    "kg": ("peso", 1.0),
    "g": ("peso", 0.001),
    "mg": ("peso", 1e-6),
    "t": ("peso", 1000.0),
    "lb": ("peso", 0.45359237),
    "oz": ("peso", 0.028349523125),
}

# Categorie speciali (riempite dai task 2-3): simbolo -> categoria
_SPECIAL_UNITS = {}
# Categoria -> handler(value, from_u, to_u) -> float | str(errore)
_SPECIAL = {}


def _is_valid_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _category_of(unit):
    if unit in _RATIO_UNITS:
        return _RATIO_UNITS[unit][0]
    return _SPECIAL_UNITS.get(unit)


def _convert_ratio(value, from_u, to_u):
    base = value * _RATIO_UNITS[from_u][1]
    return base / _RATIO_UNITS[to_u][1]


def _fmt(x):
    return f"{x:.6g}"


def convert_units(value, from_unit, to_unit):
    if not _is_valid_number(value):
        return "valore non valido"
    cat_from = _category_of(from_unit)
    cat_to = _category_of(to_unit)
    if cat_from is None:
        return f"unità '{from_unit}' non riconosciuta"
    if cat_to is None:
        return f"unità '{to_unit}' non riconosciuta"
    if cat_from != cat_to:
        return f"impossibile convertire {cat_from} in {cat_to}"
    if cat_from in _SPECIAL:
        result = _SPECIAL[cat_from](value, from_unit, to_unit)
        if isinstance(result, str):
            return result
    else:
        result = _convert_ratio(value, from_unit, to_unit)
    return f"{_fmt(value)} {from_unit} = {_fmt(result)} {to_unit}"


CONVERT_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "convert_units",
        "description": "Converte un valore tra due unità della stessa grandezza (elenco chiuso). Errore se le unità sono incompatibili.",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": "number", "description": "valore numerico da convertire"},
                "from_unit": {"type": "string", "description": "unità di partenza, es. km"},
                "to_unit": {"type": "string", "description": "unità di arrivo, es. m"},
            },
            "required": ["value", "from_unit", "to_unit"],
        },
    },
}
