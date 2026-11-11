from datetime import date

from tools import notes_repo

OGGI = date(2026, 11, 10)
DOMANI = date(2026, 11, 11)


def _db(tmp_path):
    p = str(tmp_path / "notes.db")
    notes_repo.init_db(p)
    return p


def test_add_ritorna_id_e_created_at(tmp_path):
    p = _db(tmp_path)
    nota = notes_repo.add("comprare caffè", p, today=OGGI)
    assert nota == {"id": 1, "testo": "comprare caffè", "created_at": "2026-11-10"}


def test_list_vuota_e_popolata(tmp_path):
    p = _db(tmp_path)
    assert notes_repo.list_all(p) == []
    notes_repo.add("a", p, today=OGGI)
    notes_repo.add("b", p, today=OGGI)
    righe = notes_repo.list_all(p)
    assert [r["id"] for r in righe] == [1, 2]
    assert righe[0]["updated_at"] is None


def test_get_presente_e_assente(tmp_path):
    p = _db(tmp_path)
    notes_repo.add("x", p, today=OGGI)
    assert notes_repo.get(1, p)["testo"] == "x"
    assert notes_repo.get(99, p) is None


def test_update_presente_ritorna_prima_dopo(tmp_path):
    p = _db(tmp_path)
    notes_repo.add("vecchio", p, today=OGGI)
    res = notes_repo.update(1, "nuovo", p, today=DOMANI)
    assert res == {"id": 1, "prima": "vecchio", "dopo": "nuovo", "updated_at": "2026-11-11"}
    assert notes_repo.get(1, p)["updated_at"] == "2026-11-11"


def test_update_assente_ritorna_none(tmp_path):
    p = _db(tmp_path)
    assert notes_repo.update(99, "x", p, today=OGGI) is None


def test_delete_presente_e_assente(tmp_path):
    p = _db(tmp_path)
    notes_repo.add("da cancellare", p, today=OGGI)
    assert notes_repo.delete(1, p) == {"id": 1, "testo": "da cancellare"}
    assert notes_repo.get(1, p) is None
    assert notes_repo.delete(1, p) is None
