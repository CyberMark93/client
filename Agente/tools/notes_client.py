import os
import time

import requests

NOTES_API_URL = os.environ.get("NOTES_API_URL", "http://notes-api:8000")
TIMEOUT = 5
VALID_OPS = {"add", "list", "update", "delete"}


def discover_notes_tool(base_url=None, retries=10, delay=1.0):
    url = (base_url or NOTES_API_URL).rstrip("/")
    last = None
    for _ in range(retries):
        try:
            resp = requests.get(f"{url}/tool-schema", timeout=TIMEOUT)
            resp.raise_for_status()
            return [resp.json()], {"notes_tool": notes_tool}
        except requests.RequestException as exc:
            last = exc
            time.sleep(delay)
    raise RuntimeError(f"notes-api non raggiungibile dopo {retries} tentativi: {last}")


def notes_tool(**kwargs):
    operation = kwargs.get("operation")
    if operation not in VALID_OPS:
        return (f"Operazione non riconosciuta: '{operation}'. "
                "Valide: add, list, update, delete.")
    try:
        if operation == "add":
            return _add(kwargs.get("testo"))
        if operation == "list":
            return _list()
        if operation == "update":
            return _update(kwargs.get("id"), kwargs.get("testo"))
        return _delete(kwargs.get("id"), bool(kwargs.get("conferma", False)))
    except requests.RequestException:
        return "Servizio note non raggiungibile."


def _base():
    return NOTES_API_URL.rstrip("/")


def _add(testo):
    resp = requests.post(f"{_base()}/notes", json={"testo": testo or ""}, timeout=TIMEOUT)
    if resp.status_code == 422:
        return "Per aggiungere una nota serve il testo."
    d = resp.json()
    return f"Creata nota {d['id']}: '{d['testo']}' ({d['created_at']})."


def _list():
    note = requests.get(f"{_base()}/notes", timeout=TIMEOUT).json()
    if not note:
        return "Nessuna nota salvata."
    righe = []
    for n in note:
        riga = f"{n['id']} | {n['testo']} | {n['created_at']}"
        if n.get("updated_at"):
            riga += f" (mod. {n['updated_at']})"
        righe.append(riga)
    return "\n".join(righe)


def _update(note_id, testo):
    if note_id is None:
        return "Per modificare una nota servono id e testo."
    resp = requests.put(f"{_base()}/notes/{note_id}", json={"testo": testo or ""}, timeout=TIMEOUT)
    if resp.status_code == 404:
        return f"Nessuna nota {note_id}: niente da modificare."
    if resp.status_code == 422:
        return "Per modificare una nota serve il testo."
    d = resp.json()
    return f"Nota {d['id']} aggiornata.\nprima: '{d['prima']}'\ndopo: '{d['dopo']}'"


def _delete(note_id, conferma):
    if note_id is None:
        return "Per eliminare una nota serve l'id."
    resp = requests.delete(f"{_base()}/notes/{note_id}",
                           params={"conferma": str(conferma).lower()}, timeout=TIMEOUT)
    if resp.status_code == 404:
        return f"Nessuna nota {note_id}: niente da eliminare."
    d = resp.json()
    if d.get("status") == "pending_confirmation":
        return (f"Stai per eliminare la nota {d['id']}: '{d['testo']}'. "
                "Richiama con conferma=true.")
    return f"Nota {d['id']} eliminata: '{d['testo']}'."
