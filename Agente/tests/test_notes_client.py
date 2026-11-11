import json

import pytest

from tools import notes_client


class FakeResp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise notes_client.requests.HTTPError(f"status {self.status_code}")


def test_operation_non_valida_non_fa_http(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("nessun HTTP atteso")
    monkeypatch.setattr(notes_client.requests, "post", boom)
    out = notes_client.notes_tool(operation="pippo")
    assert "Operazione non riconosciuta" in out and "add, list, update, delete" in out


def test_add_traduce_201(monkeypatch):
    monkeypatch.setattr(notes_client.requests, "post",
                        lambda *a, **k: FakeResp(201, {"id": 5, "testo": "x", "created_at": "2026-11-10"}))
    out = notes_client.notes_tool(operation="add", testo="x")
    assert out == "Creata nota 5: 'x' (2026-11-10)."


def test_add_testo_vuoto_traduce_422(monkeypatch):
    monkeypatch.setattr(notes_client.requests, "post", lambda *a, **k: FakeResp(422, {}))
    out = notes_client.notes_tool(operation="add", testo="")
    assert out == "Per aggiungere una nota serve il testo."


def test_list_vuota_e_popolata(monkeypatch):
    monkeypatch.setattr(notes_client.requests, "get", lambda *a, **k: FakeResp(200, []))
    assert notes_client.notes_tool(operation="list") == "Nessuna nota salvata."
    monkeypatch.setattr(notes_client.requests, "get",
                        lambda *a, **k: FakeResp(200, [{"id": 1, "testo": "a", "created_at": "2026-11-10", "updated_at": None}]))
    assert notes_client.notes_tool(operation="list") == "1 | a | 2026-11-10"


def test_delete_senza_conferma(monkeypatch):
    monkeypatch.setattr(notes_client.requests, "delete",
                        lambda *a, **k: FakeResp(200, {"status": "pending_confirmation", "id": 3, "testo": "ciao"}))
    out = notes_client.notes_tool(operation="delete", id=3)
    assert "Stai per eliminare la nota 3: 'ciao'" in out and "conferma=true" in out


def test_delete_con_conferma(monkeypatch):
    monkeypatch.setattr(notes_client.requests, "delete",
                        lambda *a, **k: FakeResp(200, {"status": "deleted", "id": 3, "testo": "ciao"}))
    assert notes_client.notes_tool(operation="delete", id=3, conferma=True) == "Nota 3 eliminata: 'ciao'."


def test_delete_404(monkeypatch):
    monkeypatch.setattr(notes_client.requests, "delete", lambda *a, **k: FakeResp(404, {}))
    assert notes_client.notes_tool(operation="delete", id=99) == "Nessuna nota 99: niente da eliminare."


def test_errore_collegamento(monkeypatch):
    def boom(*a, **k):
        raise notes_client.requests.ConnectionError("giù")
    monkeypatch.setattr(notes_client.requests, "get", boom)
    assert notes_client.notes_tool(operation="list") == "Servizio note non raggiungibile."


def test_discovery_costruisce_schema_e_registry(monkeypatch):
    monkeypatch.setattr(notes_client.requests, "get",
                        lambda *a, **k: FakeResp(200, {"type": "function", "function": {"name": "notes_tool"}}))
    schemas, registry = notes_client.discover_notes_tool(base_url="http://x", retries=1, delay=0)
    assert schemas[0]["function"]["name"] == "notes_tool"
    assert registry["notes_tool"] is notes_client.notes_tool


def test_grafo_instrada_notes(monkeypatch):
    import tools
    from graph import build_graph
    from tools import notes_app

    monkeypatch.setattr(notes_client.requests, "post",
                        lambda *a, **k: FakeResp(201, {"id": 1, "testo": "comprare caffè", "created_at": "2026-11-10"}))
    tools.TOOL_REGISTRY["notes_tool"] = notes_client.notes_tool
    all_tools = tools.TOOLS + [notes_app.NOTES_TOOL_SCHEMA]

    chiamata = {"role": "assistant", "content": "",
                "tool_calls": [{"id": "c1", "type": "function",
                                "function": {"name": "notes_tool",
                                             "arguments": json.dumps({"operation": "add", "testo": "comprare caffè"})}}]}
    risposte = [chiamata, {"role": "assistant", "content": "Fatto."}]

    def fake_llm(messages, tools_arg):
        return risposte.pop(0)

    g = build_graph(fake_llm, tools=all_tools)
    out = g.invoke({"messages": [{"role": "user", "content": "aggiungi nota"}], "steps": 0})
    assert [m["role"] for m in out["messages"]] == ["user", "assistant", "tool", "assistant"]
    assert "Creata nota 1" in out["messages"][2]["content"]
