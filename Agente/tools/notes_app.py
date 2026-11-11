import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

from tools import notes_repo

NOTES_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "notes_tool",
        "description": (
            "Gestisce note personali persistenti. operation='add' aggiunge una nota "
            "(richiede testo); 'list' elenca tutte le note; 'update' modifica il testo di "
            "una nota (richiede id e testo); 'delete' elimina una nota (richiede id; va "
            "richiamato con conferma=true per eseguire davvero)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["add", "list", "update", "delete"]},
                "testo": {"type": "string"},
                "id": {"type": "integer"},
                "conferma": {"type": "boolean"},
            },
            "required": ["operation"],
        },
    },
}


class NoteIn(BaseModel):
    testo: str

    @field_validator("testo")
    @classmethod
    def non_vuoto(cls, v):
        if not v or not v.strip():
            raise ValueError("testo vuoto")
        return v


def _db_path():
    return os.environ.get("NOTES_DB_PATH", notes_repo.DEFAULT_DB_PATH)


@asynccontextmanager
async def lifespan(app):
    notes_repo.init_db(_db_path())
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tool-schema")
def tool_schema():
    return NOTES_TOOL_SCHEMA


@app.post("/notes", status_code=201)
def create_note(nota: NoteIn):
    return notes_repo.add(nota.testo, _db_path())


@app.get("/notes")
def list_notes():
    return notes_repo.list_all(_db_path())


@app.put("/notes/{note_id}")
def update_note(note_id: int, nota: NoteIn):
    res = notes_repo.update(note_id, nota.testo, _db_path())
    if res is None:
        raise HTTPException(status_code=404, detail=f"nota {note_id} non trovata")
    return res


@app.delete("/notes/{note_id}")
def delete_note(note_id: int, conferma: bool = False):
    nota = notes_repo.get(note_id, _db_path())
    if nota is None:
        raise HTTPException(status_code=404, detail=f"nota {note_id} non trovata")
    if not conferma:
        return {"status": "pending_confirmation", "id": note_id, "testo": nota["testo"]}
    res = notes_repo.delete(note_id, _db_path())
    return {"status": "deleted", "id": res["id"], "testo": res["testo"]}
