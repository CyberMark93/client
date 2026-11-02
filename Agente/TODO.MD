# TODO / Resoconto — Agente

> File locale (gitignore): alla consegna incluso coscientemente con `git add -f` (scelta utente).

## Resoconto finale: stato incrementi
- [x] **Igrafo a risposta fissa**: `State{messages (operator.add), steps}`, `call_model`, `build_graph`.
- [x] **LM Studio + cronologia**: `config.py`, `llm.py` (non-streaming, errori distinti), `app.py` (`handle_turn`/`run_chat`/`main`, cronologia in memoria).
- [x] **strumento orologio**: `tools.py` (`get_current_time` via `zoneinfo`), nodo `tools`, `should_continue`, instradamento condizionato, `MAX_STEPS=3`.
- [x] **Docker**: `Dockerfile` (`python:3.14-slim`), `.dockerignore`, `docker-compose.yml` (rotta `host.docker.internal`, variabili d'ambiente), `config.py` adeguato all'ambiente del container.

## Prove reali eseguite (separate dai test automatici)
- [x] **Test automatici**: `pytest` → **14 passed** (eseguiti nel container Linux; vedi nota SAC).
- [x] **Build Docker**: `docker build` → OK, tutte le wheel cp314 disponibili (nessuna compilazione).
- [x] **Chat multi-turno** (cronologia): il modello ha richiamato dati forniti solo al turno precedente.
- [x] **Tool-call reale orologio**: «Che ore sono a Roma?» → `tool-call get_current_time({'timezone':'Europe/Rome'})` nei log → `+01:00` → risposta coerente.
- [x] **Rete container → host**: la chat dal container raggiunge LM Studio sull'host via `host.docker.internal:1234`.
- [x] **Correttezza fusi (DST-aware)** allo stesso istante: Roma +01:00, New York −05:00, Tokyo +09:00, Los Angeles −08:00, Sydney +11:00; fuso invalido → messaggio d'errore.

## Commits
- Committati: (`feat(config)`), (`feat(llm)`).
- **Pendenti (azione utente, staging selettivo):** (`feat(app)`),(`feat(docker): Dockerfile`), (`feat(docker): compose + config`), (`feat(strumenti)` + `feat(grafo): nodo tools`), (`docs`).

## Problemi aperti / note
- **Smart App Control (Windows)**: in *enforce* blocca l'esecuzione **locale** su `_xxhash.pyd` (DLL
  non firmata, dipendenza transitiva di langgraph). Verifica e avvio fatti via **Docker** (Linux, non
  soggetto a SAC). Nessun impatto sul deliverable.
- **Doc**: la spec §4.2 mostrava `add_messages`; piano e codice usano `operator.add` (messaggi come
  dict OpenAI grezzi). Scelta mantenuta: `operator.add`.
- **`client.py`** (traccia esplicativa, mai committata): da decidere se eliminare a fine lavori.

