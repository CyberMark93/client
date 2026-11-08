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
    # tempo (base: s)
    "s": ("tempo", 1.0), "ms": ("tempo", 0.001), "min": ("tempo", 60.0),
    "h": ("tempo", 3600.0), "giorno": ("tempo", 86400.0),
    # volume (base: L)
    "L": ("volume", 1.0), "mL": ("volume", 0.001), "m3": ("volume", 1000.0),
    "gal": ("volume", 3.785411784),
    # area (base: m2)
    "m2": ("area", 1.0), "km2": ("area", 1e6), "cm2": ("area", 1e-4),
    "ha": ("area", 1e4), "acre": ("area", 4046.8564224),
    # velocità (base: m/s)
    "m/s": ("velocità", 1.0), "km/h": ("velocità", 1 / 3.6), "mph": ("velocità", 0.44704),
    "nodo": ("velocità", 1852 / 3600),
    # pressione (base: Pa)
    "Pa": ("pressione", 1.0), "kPa": ("pressione", 1000.0), "bar": ("pressione", 1e5),
    "atm": ("pressione", 101325.0), "psi": ("pressione", 6894.757293168),
    # energia (base: J)
    "J": ("energia", 1.0), "kJ": ("energia", 1000.0), "cal": ("energia", 4.184),
    "kcal": ("energia", 4184.0), "kWh": ("energia", 3.6e6),
    # angolo (base: rad)
    "rad": ("angolo", 1.0), "grado": ("angolo", math.pi / 180), "grad": ("angolo", math.pi / 200),
    "giro": ("angolo", 2 * math.pi),
    # dati digitali (base: B)
    "B": ("dati", 1.0), "bit": ("dati", 0.125), "KB": ("dati", 1000.0), "MB": ("dati", 1e6),
    "GB": ("dati", 1e9), "KiB": ("dati", 1024.0), "MiB": ("dati", 1048576.0), "GiB": ("dati", 1073741824.0),
    # potenza (base: W)
    "W": ("potenza", 1.0), "kW": ("potenza", 1000.0), "MW": ("potenza", 1e6),
    "hp": ("potenza", 745.6998715822702), "CV": ("potenza", 735.49875),
    # frequenza (base: Hz)
    "Hz": ("frequenza", 1.0), "kHz": ("frequenza", 1000.0), "MHz": ("frequenza", 1e6),
    "GHz": ("frequenza", 1e9), "rpm": ("frequenza", 1 / 60),
    # forza (base: N)
    "N": ("forza", 1.0), "kN": ("forza", 1000.0), "kgf": ("forza", 9.80665),
    "lbf": ("forza", 4.4482216152605),
    # densità (base: kg/m3)
    "kg/m3": ("densità", 1.0), "g/cm3": ("densità", 1000.0), "g/L": ("densità", 1.0),
    "lb/ft3": ("densità", 16.018463373960142),
    # portata (base: m3/s)
    "m3/s": ("portata", 1.0), "L/s": ("portata", 0.001), "L/min": ("portata", 0.001 / 60),
    "m3/h": ("portata", 1 / 3600), "gpm": ("portata", 3.785411784e-3 / 60),
    # velocità angolare (base: rad/s)
    "rad/s": ("vel_angolare", 1.0), "giri/min": ("vel_angolare", 2 * math.pi / 60),
    "°/s": ("vel_angolare", math.pi / 180), "giri/s": ("vel_angolare", 2 * math.pi),
    # accelerazione (base: m/s2) — NOTA: gravità standard = g0 (g è già grammi)
    "m/s2": ("accelerazione", 1.0), "g0": ("accelerazione", 9.80665), "ft/s2": ("accelerazione", 0.3048),
    # coppia (base: N·m)
    "N·m": ("coppia", 1.0), "kgf·m": ("coppia", 9.80665), "lbf·ft": ("coppia", 1.3558179483314004),
    # velocità dati (base: bit/s)
    "bit/s": ("vel_dati", 1.0), "kbit/s": ("vel_dati", 1000.0), "Mbit/s": ("vel_dati", 1e6),
    "Gbit/s": ("vel_dati", 1e9), "B/s": ("vel_dati", 8.0), "MB/s": ("vel_dati", 8e6),
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


def _to_kelvin(value, unit):
    if unit == "°C":
        return value + 273.15
    if unit == "°F":
        return (value - 32.0) * 5.0 / 9.0 + 273.15
    return value  # K


def _from_kelvin(k, unit):
    if unit == "°C":
        return k - 273.15
    if unit == "°F":
        return (k - 273.15) * 9.0 / 5.0 + 32.0
    return k  # K


def _temp_handler(value, from_u, to_u):
    k = _to_kelvin(value, from_u)
    if k < -1e-9:
        return "temperatura sotto lo zero assoluto"
    return _from_kelvin(k, to_u)


for _u in ("°C", "°F", "K"):
    _SPECIAL_UNITS[_u] = "temperatura"
_SPECIAL["temperatura"] = _temp_handler


_MPG_TO_KMPL = 1.609344 / 3.785411784  # mpg(US) -> km/L


def _fuel_to_kmpl(value, unit):
    if unit == "km/L":
        return value
    if unit == "L/100km":
        return 100.0 / value
    return value * _MPG_TO_KMPL  # mpg


def _fuel_from_kmpl(kmpl, unit):
    if unit == "km/L":
        return kmpl
    if unit == "L/100km":
        return 100.0 / kmpl
    return kmpl / _MPG_TO_KMPL  # mpg


def _fuel_handler(value, from_u, to_u):
    if value <= 0:
        return "valore non valido"
    return _fuel_from_kmpl(_fuel_to_kmpl(value, from_u), to_u)


for _u in ("km/L", "L/100km", "mpg"):
    _SPECIAL_UNITS[_u] = "consumo"
_SPECIAL["consumo"] = _fuel_handler


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
