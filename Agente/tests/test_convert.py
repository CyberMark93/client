import convert


def test_rapporto_lunghezza():
    assert convert.convert_units(2.5, "km", "m") == "2.5 km = 2500 m"


def test_rapporto_peso():
    assert convert.convert_units(1, "kg", "g") == "1 kg = 1000 g"


def test_unita_sconosciuta():
    assert convert.convert_units(1, "xyz", "m") == "unità 'xyz' non riconosciuta"


def test_incompatibile():
    assert convert.convert_units(1, "m", "kg") == "impossibile convertire lunghezza in peso"


def test_valore_non_valido():
    assert convert.convert_units(float("inf"), "m", "km") == "valore non valido"


def test_schema_ben_formato():
    s = convert.CONVERT_TOOL_SCHEMA
    assert s["function"]["name"] == "convert_units"
    assert s["function"]["parameters"]["required"] == ["value", "from_unit", "to_unit"]


def test_temp_c_to_f():
    assert convert.convert_units(100, "°C", "°F") == "100 °C = 212 °F"


def test_temp_f_to_c():
    assert convert.convert_units(32, "°F", "°C") == "32 °F = 0 °C"


def test_temp_c_to_k():
    assert convert.convert_units(0, "°C", "K") == "0 °C = 273.15 K"


def test_temp_zero_assoluto():
    assert convert.convert_units(-300, "°C", "K") == "temperatura sotto lo zero assoluto"


def test_consumo_kmpl_to_l100km():
    assert convert.convert_units(20, "km/L", "L/100km") == "20 km/L = 5 L/100km"


def test_consumo_l100km_to_kmpl():
    assert convert.convert_units(5, "L/100km", "km/L") == "5 L/100km = 20 km/L"


def test_consumo_valore_non_positivo():
    assert convert.convert_units(0, "km/L", "L/100km") == "valore non valido"


import pytest


@pytest.mark.parametrize("value,from_u,to_u,expected", [
    (2, "h", "min", "2 h = 120 min"),
    (1, "m3", "L", "1 m3 = 1000 L"),
    (1, "ha", "m2", "1 ha = 10000 m2"),
    (36, "km/h", "m/s", "36 km/h = 10 m/s"),
    (1, "bar", "Pa", "1 bar = 100000 Pa"),
    (1, "kcal", "cal", "1 kcal = 1000 cal"),
    (180, "grado", "rad", "180 grado = 3.14159 rad"),
    (1, "KB", "B", "1 KB = 1000 B"),
    (1, "KiB", "B", "1 KiB = 1024 B"),
    (1, "kW", "W", "1 kW = 1000 W"),
    (1, "kHz", "Hz", "1 kHz = 1000 Hz"),
    (1, "kN", "N", "1 kN = 1000 N"),
    (1, "g/cm3", "kg/m3", "1 g/cm3 = 1000 kg/m3"),
    (1, "L/s", "m3/h", "1 L/s = 3.6 m3/h"),
    (360, "°/s", "giri/s", "360 °/s = 1 giri/s"),
    (1, "g0", "m/s2", "1 g0 = 9.80665 m/s2"),
    (1, "kgf·m", "N·m", "1 kgf·m = 9.80665 N·m"),
    (1, "B/s", "bit/s", "1 B/s = 8 bit/s"),
])
def test_categorie_a_rapporto(value, from_u, to_u, expected):
    assert convert.convert_units(value, from_u, to_u) == expected


import json

import tools
from graph import build_graph


def test_registry_espone_convert_units():
    assert tools.TOOL_REGISTRY["convert_units"] is convert.convert_units


def test_grafo_instrada_convert_units():
    chiamata = {
        "role": "assistant", "content": "",
        "tool_calls": [{"id": "c1", "type": "function",
                        "function": {"name": "convert_units",
                                     "arguments": json.dumps({"value": 2.5, "from_unit": "km", "to_unit": "m"})}}],
    }
    risposte = [chiamata, {"role": "assistant", "content": "2500 metri."}]

    def fake_llm(messages, tools_arg):
        return risposte.pop(0)

    g = build_graph(fake_llm, tools=tools.TOOLS)
    out = g.invoke({"messages": [{"role": "user", "content": "converti"}], "steps": 0})
    roles = [m["role"] for m in out["messages"]]
    assert roles == ["user", "assistant", "tool", "assistant"]
    assert out["messages"][2]["content"] == "2.5 km = 2500 m"
