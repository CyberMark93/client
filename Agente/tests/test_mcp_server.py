from tools import mcp_server

ITEMS = [
    {"id": "MIS-001", "nome": "Multimetro digitale", "categoria": "misura",
     "descrizione": "Misura tensione, corrente, resistenza.", "quantita_disponibile": 4},
    {"id": "MIS-002", "nome": "Oscilloscopio", "categoria": "misura",
     "descrizione": "Visualizza segnali nel tempo.", "quantita_disponibile": 1},
    {"id": "UTE-010", "nome": "Saldatore", "categoria": "utensili",
     "descrizione": "Saldatura a stagno.", "quantita_disponibile": 7},
]


def test_search_match():
    out = mcp_server._search("multimetro", ITEMS)
    assert out == "MIS-001 — Multimetro digitale (misura)"


def test_search_per_categoria():
    out = mcp_server._search("misura", ITEMS)
    assert "MIS-001" in out and "MIS-002" in out and "UTE-010" not in out


def test_search_vuoto():
    assert mcp_server._search("inesistente", ITEMS) == "nessuno strumento trovato per 'inesistente'"


def test_get_trovato():
    out = mcp_server._get("UTE-010", ITEMS)
    assert "UTE-010 — Saldatore" in out and "disponibili: 7" in out


def test_get_non_trovato():
    assert mcp_server._get("ZZZ-999", ITEMS) == "strumento non trovato: ZZZ-999"


def test_catalog_json_caricabile():
    items = mcp_server._load_catalog()
    assert isinstance(items, list) and len(items) >= 5
    assert all({"id", "nome", "categoria", "quantita_disponibile"} <= set(it) for it in items)
