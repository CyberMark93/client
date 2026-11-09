from tools import mcp_client


def test_discovery_schemi_openai():
    schemas, registry = mcp_client.discover_mcp_tools()
    names = {s["function"]["name"] for s in schemas}
    assert {"search_catalog", "get_item"} <= names
    for s in schemas:
        assert s["type"] == "function"
        assert "parameters" in s["function"]
    assert set(registry.keys()) == names


def test_call_search_catalog_reale():
    out = mcp_client.call_mcp_tool("search_catalog", {"query": "multimetro"})
    assert "MIS-001" in out and "Multimetro" in out


def test_call_get_item_reale():
    out = mcp_client.call_mcp_tool("get_item", {"item_id": "UTE-010"})
    assert "Saldatore" in out and "disponibili: 7" in out


def test_call_ricerca_vuota_reale():
    out = mcp_client.call_mcp_tool("search_catalog", {"query": "zzz-inesistente"})
    assert out == "nessuno strumento trovato per 'zzz-inesistente'"


def test_wrapper_registry_invoca_mcp():
    _, registry = mcp_client.discover_mcp_tools()
    out = registry["get_item"](item_id="MIS-002")
    assert "Oscilloscopio" in out
