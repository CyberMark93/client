# Assistente del laboratorio

App da terminale in Python che conversa con un modello locale servito da **LM Studio**,
orchestrata da un grafo **LangGraph** esplicito. Offre uno strumento **orologio** con fuso
orario esplicito, richiesto dal modello via *tool calling* ed eseguito dal programma.
Si avvia anche con **Docker Compose**.

- Cronologia della conversazione tenuta in memoria per la durata della sessione (nessuna persistenza).
- Non-streaming, chat-only. Parola di uscita: `esci`.
- Limite di `MAX_STEPS = 3` chiamate al modello per turno.
- `State = {messages (reducer operator.add), steps}`.
- `config.py` legge `LM_BASE_URL`, `LM_MODEL` da `.env` (locale) o dalle variabili d'ambiente (Docker).

## Prerequisiti
- **LM Studio** sull'host: modello caricato, server avviato (`localhost:1234`), con
  l'opzione **"Serve on Local Network"** attiva (serve al container per raggiungere l'host).
- L'ID del modello è quello restituito da `GET /v1/models` (mai inventato). Verificato in questo
  progetto: `google/gemma-4-e2b`.
- Per l'avvio via Docker: **Docker Desktop** attivo.
- Per l'esecuzione/test locali: **Python 3.14**.

## Avvio via Docker Compose (consegna)
Da PowerShell, nella cartella `Agente/`:
```powershell
docker compose run --rm app
```
Si apre la chat interattiva. Esempio:
```
Tu> Che ore sono adesso a Roma?
INFO graph: tool-call   get_current_time({'timezone': 'Europe/Rome'})
INFO graph: tool-result get_current_time -> 2026-11-02T11:16:14+01:00 (Europe/Rome)
Assistente> Adesso sono le 11:16:14 del 2 novembre 2026 a Roma.
Tu> esci
```
Le variabili (`LM_BASE_URL`, `LM_MODEL`) e la rotta `host.docker.internal` sono già in
`docker-compose.yml`; il container non usa `.env`.

## Avvio locale (senza Docker)
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env   # poi compila LM_BASE_URL e LM_MODEL
.\.venv\Scripts\python.exe app.py
```

## Test automatici (senza modello attivo)
I test non richiedono LM Studio. Comando locale:
```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -v
```
Esecuzione equivalente dentro il container (utile se l'ambiente locale blocca estensioni native —
vedi *Diagnosi*):
```powershell
docker run --rm -v "${PWD}:/src" -w /src assistente-lab sh -c "pip install -q pytest; python -m pytest -v"
```
Esito verificato: **14 passed**.

## Diagnosi
- **Connessione fallita / HTTP error**: `llm.py` esce con messaggio distinto (timeout, connessione,
  HTTP non-200). Controllare che LM Studio sia avviato e raggiungibile.
- **Config mancante**: `config.py` esce indicando quali variabili mancano.
- **Dal container non raggiunge LM Studio**: attivare "Serve on Local Network" in LM Studio; la
  rotta `host.docker.internal:host-gateway` è già in `docker-compose.yml`.
- **Windows Smart App Control**: su macchine con SAC in *enforce*, l'esecuzione **locale** può essere
  bloccata su una DLL nativa non firmata (`_xxhash.pyd`, dipendenza transitiva di langgraph). In tal
  caso usare il percorso **Docker** (Linux, non soggetto a SAC) per test e avvio.
