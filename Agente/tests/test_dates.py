import dates


def test_weekday():
    assert dates.date_tool("weekday", start="2026-12-25") == "2026-12-25 è venerdì"


def test_add_days():
    assert dates.date_tool("add_days", start="2026-11-09", days=30) == "2026-11-09 + 30 giorni = 2026-12-09"


def test_add_days_negativo():
    assert dates.date_tool("add_days", start="2026-12-09", days=-30) == "2026-12-09 + -30 giorni = 2026-11-09"


def test_days_between():
    assert dates.date_tool("days_between", start="2026-11-09", end="2026-12-25") == "da 2026-11-09 a 2026-12-25: 46 giorni"


def test_days_between_segno_negativo():
    assert dates.date_tool("days_between", start="2026-12-25", end="2026-11-09") == "da 2026-12-25 a 2026-11-09: -46 giorni"


def test_bisestile_29_feb_valida():
    assert dates.date_tool("weekday", start="2028-02-29").startswith("2028-02-29 è ")


def test_29_feb_non_bisestile_invalida():
    assert dates.date_tool("weekday", start="2026-02-29") == "data non valida: 2026-02-29"


def test_data_non_valida():
    assert dates.date_tool("weekday", start="2026-13-01") == "data non valida: 2026-13-01"


def test_operazione_ignota():
    assert dates.date_tool("foo", start="2026-01-01") == "operazione non riconosciuta: foo"


def test_argomento_mancante():
    assert dates.date_tool("weekday") == "argomento mancante per weekday"


def test_days_non_valido():
    assert dates.date_tool("add_days", start="2026-01-01") == "numero di giorni non valido"


def test_schema_ben_formato():
    s = dates.DATE_TOOL_SCHEMA
    assert s["function"]["name"] == "date_tool"
    assert s["function"]["parameters"]["required"] == ["operation"]
    assert "deadline" in s["function"]["parameters"]["properties"]["operation"]["enum"]


import datetime

import pytest


def test_load_txt(tmp_path):
    p = tmp_path / "h.txt"
    p.write_text("# commento\n2026-12-25 Natale\n\n2026-01-01\n", encoding="utf-8")
    assert dates.load_holidays(str(p)) == {datetime.date(2026, 12, 25), datetime.date(2026, 1, 1)}


def test_load_csv(tmp_path):
    p = tmp_path / "h.csv"
    p.write_text("data,nome\n2026-12-25,Natale\n2026-01-01,Capodanno\n", encoding="utf-8")
    assert dates.load_holidays(str(p)) == {datetime.date(2026, 12, 25), datetime.date(2026, 1, 1)}


def test_load_json(tmp_path):
    p = tmp_path / "h.json"
    p.write_text('[{"date":"2026-12-25","name":"Natale"},"2026-01-01"]', encoding="utf-8")
    assert dates.load_holidays(str(p)) == {datetime.date(2026, 12, 25), datetime.date(2026, 1, 1)}


def test_load_malformato(tmp_path):
    p = tmp_path / "h.txt"
    p.write_text("2026-99-99\n", encoding="utf-8")
    with pytest.raises(ValueError):
        dates.load_holidays(str(p))


def test_load_estensione_non_supportata(tmp_path):
    p = tmp_path / "h.xml"
    p.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        dates.load_holidays(str(p))


def test_holidays_file_esempio_caricabile():
    h = dates.load_holidays(dates.HOLIDAYS_PATH)
    assert datetime.date(2026, 12, 25) in h


def test_business_days_between_iniettato():
    hol = {datetime.date(2026, 12, 25)}
    assert dates.date_tool("business_days_between", start="2026-12-21", end="2026-12-28", holidays=hol) \
        == "da 2026-12-21 a 2026-12-28: 4 giorni lavorativi"


def test_business_days_intervallo_invertito():
    assert dates.date_tool("business_days_between", start="2026-12-28", end="2026-12-21", holidays=set()) \
        == "intervallo invertito"


def test_deadline_iniettato():
    hol = {datetime.date(2026, 12, 25)}
    assert dates.date_tool("deadline", start="2026-12-23", days=3, holidays=hol) \
        == "scadenza: 3 giorni lavorativi dopo 2026-12-23 = 2026-12-29"


def test_deadline_giorni_non_positivi():
    assert dates.date_tool("deadline", start="2026-12-23", days=0, holidays=set()) \
        == "i giorni devono essere positivi"


def test_business_days_usa_file_default():
    out = dates.date_tool("business_days_between", start="2026-12-21", end="2026-12-28")
    assert out == "da 2026-12-21 a 2026-12-28: 4 giorni lavorativi"


import json as _json

import tools
from graph import build_graph


def test_registry_espone_date_tool():
    assert tools.TOOL_REGISTRY["date_tool"] is dates.date_tool


def test_grafo_instrada_date_tool():
    chiamata = {
        "role": "assistant", "content": "",
        "tool_calls": [{"id": "c1", "type": "function",
                        "function": {"name": "date_tool",
                                     "arguments": _json.dumps({"operation": "weekday", "start": "2026-12-25"})}}],
    }
    risposte = [chiamata, {"role": "assistant", "content": "È venerdì."}]

    def fake_llm(messages, tools_arg):
        return risposte.pop(0)

    g = build_graph(fake_llm, tools=tools.TOOLS)
    out = g.invoke({"messages": [{"role": "user", "content": "che giorno"}], "steps": 0})
    roles = [m["role"] for m in out["messages"]]
    assert roles == ["user", "assistant", "tool", "assistant"]
    assert out["messages"][2]["content"] == "2026-12-25 è venerdì"
