import pytest
import requests
import llm


class FakeResp:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


def test_call_llm_ritorna_il_messaggio_assistant(monkeypatch):
    payload = {"choices": [{"message": {"role": "assistant", "content": "ok"}}]}
    monkeypatch.setattr(requests, "post", lambda *a, **k: FakeResp(200, payload))
    msg = llm.call_llm("http://x/v1", "m", [{"role": "user", "content": "ciao"}])
    assert msg == {"role": "assistant", "content": "ok"}


def test_call_llm_http_error_esce_con_messaggio(monkeypatch):
    monkeypatch.setattr(requests, "post", lambda *a, **k: FakeResp(400, text="bad"))
    with pytest.raises(SystemExit):
        llm.call_llm("http://x/v1", "m", [])


def test_call_llm_connessione_fallita_esce(monkeypatch):
    def boom(*a, **k):
        raise requests.exceptions.ConnectionError()
    monkeypatch.setattr(requests, "post", boom)
    with pytest.raises(SystemExit):
        llm.call_llm("http://x/v1", "m", [])
