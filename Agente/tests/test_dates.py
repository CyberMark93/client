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
