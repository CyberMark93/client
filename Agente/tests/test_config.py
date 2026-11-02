import pytest
import config


def test_load_config_legge_le_due_variabili(tmp_path, monkeypatch):
    monkeypatch.delenv("LM_BASE_URL", raising=False)
    monkeypatch.delenv("LM_MODEL", raising=False)
    env = tmp_path / ".env"
    env.write_text("LM_BASE_URL=http://localhost:1234/v1\nLM_MODEL=google/gemma-4-e2b\n", encoding="utf-8")
    assert config.load_config(str(env)) == ("http://localhost:1234/v1", "google/gemma-4-e2b")


def test_load_config_esce_se_file_assente(tmp_path, monkeypatch):
    monkeypatch.delenv("LM_BASE_URL", raising=False)
    monkeypatch.delenv("LM_MODEL", raising=False)
    with pytest.raises(SystemExit):
        config.load_config(str(tmp_path / "manca.env"))


def test_load_config_usa_env_se_file_assente(tmp_path, monkeypatch):
    monkeypatch.setenv("LM_BASE_URL", "http://host.docker.internal:1234/v1")
    monkeypatch.setenv("LM_MODEL", "google/gemma-4-e2b")
    assert config.load_config(str(tmp_path / "assente.env")) == (
        "http://host.docker.internal:1234/v1", "google/gemma-4-e2b")
