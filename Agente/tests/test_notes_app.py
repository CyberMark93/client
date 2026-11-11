import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = str(tmp_path / "notes.db")
    monkeypatch.setenv("NOTES_DB_PATH", db)
    from tools import notes_repo, notes_app
    notes_repo.init_db(db)
    return TestClient(notes_app.app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


def test_tool_schema_dal_server(client):
    r = client.get("/tool-schema")
    assert r.status_code == 200
    body = r.json()
    assert body["function"]["name"] == "notes_tool"
    assert body["function"]["parameters"]["required"] == ["operation"]
    assert set(body["function"]["parameters"]["properties"]["operation"]["enum"]) == {
        "add", "list", "update", "delete"}


def test_add_poi_list(client):
    r = client.post("/notes", json={"testo": "comprare caffè"})
    assert r.status_code == 201
    assert r.json()["id"] == 1 and r.json()["testo"] == "comprare caffè"
    assert client.get("/notes").json()[0]["testo"] == "comprare caffè"


def test_add_testo_vuoto_422(client):
    assert client.post("/notes", json={"testo": "   "}).status_code == 422


def test_update_e_404(client):
    client.post("/notes", json={"testo": "vecchio"})
    r = client.put("/notes/1", json={"testo": "nuovo"})
    assert r.status_code == 200 and r.json()["prima"] == "vecchio" and r.json()["dopo"] == "nuovo"
    assert client.put("/notes/99", json={"testo": "x"}).status_code == 404


def test_delete_senza_conferma_non_cancella(client):
    client.post("/notes", json={"testo": "importante"})
    r = client.delete("/notes/1")
    assert r.status_code == 200 and r.json()["status"] == "pending_confirmation"
    assert len(client.get("/notes").json()) == 1  # la nota resta: non cancellata


def test_delete_con_conferma_cancella(client):
    client.post("/notes", json={"testo": "importante"})
    r = client.delete("/notes/1", params={"conferma": "true"})
    assert r.status_code == 200 and r.json()["status"] == "deleted"
    assert client.get("/notes").json() == []


def test_delete_id_inesistente_404(client):
    assert client.delete("/notes/99").status_code == 404
