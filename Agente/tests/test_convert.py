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
