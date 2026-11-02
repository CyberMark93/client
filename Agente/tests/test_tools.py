from datetime import datetime
import tools


def test_get_current_time_istante_controllato():
    out = tools.get_current_time("Europe/Rome", now=datetime(2026, 1, 1, 12, 0, 0))
    assert out == "2026-01-01T12:00:00+01:00 (Europe/Rome)"


def test_get_current_time_fuso_invalido():
    out = tools.get_current_time("Non/Esiste")
    assert "non valido" in out.lower()


def test_registry_espone_lo_strumento():
    assert tools.TOOL_REGISTRY["get_current_time"] is tools.get_current_time
