# Assistente del laboratorio
Progetto del corso «Deep Learning e LLM: costruire chatbot e agenti».
Cartella del progetto: `Agente/`. Contiene l'assistente da terminale (fase orologio,
conclusa) che ora viene **esteso** con nuovi strumenti, senza ricominciare.

## Obiettivo
Applicazione da terminale in Python con un grafo LangGraph esplicito che conversa con
un modello locale (LM Studio) e:
- organizza il flusso in un grafo esplicito (stato, nodi, instradamento riconoscibili);
- conserva la cronologia della conversazione per la sessione (nessuna persistenza);
- espone strumenti richiesti dal modello via tool calling ed eseguiti davvero dal
  programma, con un limite ai passaggi;
- si avvia con Docker Compose.

**Fase corrente — 6 strumenti, uno alla volta.** Ogni strumento usa **una** variante
di trasporto ("una variante attiva" nel nodo strumenti):
- **Locale** (funzione Python in-process): 1 Convertitore di unità, 2 Calcolatrice
  sicura (senza `eval`), 3 Giorni e scadenze.
- **FastAPI** (servizio HTTP): 5 Note persistenti (SQLite).
- **FastMCP** (server MCP, discovery + invocazione): 4 Catalogo locale, 6 Meteo da API
  pubblica.
Per ogni strumento: nome, descrizione, argomenti, risultato e casi d'errore definiti;
discovery e invocazione collegati al grafo; richiesta del modello conservata **prima**
del risultato; correlazione richiesta↔risultato (ToolMessage); log e limite passi
mantenuti.

## Confini
- Implementare solo i requisiti concordati, **uno strumento alla volta**. In scope ora:
  strumenti Locale, FastAPI e FastMCP come sopra. Fuori scope: RAG, workflow oltre il
  grafo esistente, interfacce grafiche, servizi cloud, framework non concordati.
- Non anticipare funzionalità non richieste.
- Lavorare solo dentro `Agente/`. La repository contiene altre lezioni: non leggerle per
  copiarne il codice e non modificarle.
- Estendere codice e grafo esistenti; non ricominciare da una nuova applicazione.

## Scelte tecniche
- Python, moduli piccoli, separazione tra grafo, collegamento al modello, strumenti e
  interfaccia da terminale.
- **Core sincrono.** I tool MCP introducono un confine **async** esplicito (client MCP)
  con ciclo di vita della connessione gestito; l'asincronia resta confinata al trasporto
  MCP e non invade il resto del codice.
- **Un backend per trasporto, non per strumento**; **un solo** `CLAUDE.md` (niente
  CLAUDE.md per cartella-tool). Struttura indicativa, rifinita in spec:
  `tools/local.py` (tool Locale), `tools/fastapi_app.py` (una app, un endpoint per tool),
  `tools/mcp_server.py` (un server FastMCP), `tools/registry.py` (mappa nome-tool →
  trasporto attivo).
- Nodo strumenti generico (dispatch per nome): distinguere errore dello strumento,
  errore di collegamento e interpretazione errata del modello; produrre sempre un esito,
  anche quando l'esecuzione fallisce.
- LM Studio sull'host, API compatibile con OpenAI. Indirizzo server e ID modello solo da
  variabili d'ambiente; l'ID è quello restituito da `GET /v1/models`, mai inventato.
- Un file di configurazione di esempio senza credenziali; il reale resta fuori da Git.
- Docker Compose per l'applicazione; LM Studio non va containerizzato.
- Dipendenze (incluse FastAPI, server ASGI, SDK/client MCP) motivate, concordate e con
  **versioni fissate**.
- Comandi documentati anche per PowerShell (Windows).

## Metodo: Superpowers
- Brainstorming → specifica → piano → implementazione → verifica con le skill di
  Superpowers.
- Non scrivere codice prima che io abbia approvato la specifica e poi il piano.
- Salvare specifica e piano in `Agente/docs/superpowers/`.
- Procedere per incrementi piccoli, uno strumento alla volta, ciascuno verificato prima
  del commit.

## Test e verifiche
- Test automatici ripetibili **senza modello attivo** (grafo, cronologia, instradamento,
  strumento con input controllato).
- Per ogni strumento, dimostrare i sei controlli: **discovery** (nome/descrizione/schema
  dal server), **invocazione diretta** (risultato coerente con input noto),
  **integrazione nell'agente** (richiesta, argomenti, esecuzione, ToolMessage correlato),
  **errore controllato** (messaggio comprensibile, niente falso successo),
  **continuità** (cronologia e limite passi ancora funzionanti), **riproducibilità**
  (comandi, dipendenze, configurazione senza segreti).
- Prove reali con LM Studio e con Docker, separate e attivate esplicitamente. Una
  risposta simulata non dimostra che il modello sappia selezionare lo strumento.
- **Vincolo d'ambiente:** Smart App Control blocca l'esecuzione locale del codice che
  importa langgraph → **ogni verifica passa dal container Docker (Linux)**.
- Se la prova reale fallisce, **registrare il punto esatto** senza dichiarare completato
  l'intero percorso. Nel resoconto: cosa eseguito, con quale esito, cosa resta da provare.

## Git
- Conventional Commits in italiano (`feat(tool): ...`, `test(strumenti): ...`, `docs: ...`).
- **Un ramo per strumento:** `feature_branch_tool-N-<slug>` (es.
  `feature_branch_tool-1-convertitore`). Ciclo: ramo da `main` → commit → convalida →
  **merge `--no-ff` in `main`** → eliminare il ramo. Un solo ramo vivo per volta; `main`
  contiene solo strumenti finiti e verificati.
- **Git lo esegue solo l'utente, a mano.** Claude fornisce i comandi esatti e guida; non
  lancia mai git di propria iniziativa. Push soltanto su richiesta dell'utente.
- Prima di ogni commit: `git status`, controllo del diff, **staging selettivo** dei soli
  file pertinenti; mai `git add -A`/`git add .`. Mai versionare credenziali, `.env`,
  ambienti virtuali, cache o pesi dei modelli.

## Documentazione
- Tenere aggiornato il README (configurazione, avvio, test, diagnosi) con soli comandi
  verificati.
- Aggiornare questo file quando cambiano convenzioni stabili (struttura, comandi, regole
  di lavoro), non per annotare l'avanzamento.

- (lavoriamo sempre su `Agente/` salvo mia esplicita richiesta).
- fammi le domande necessarie alla costruzione del progetto rispetto a ciò che non so;
  lavoriamo step by step e io convalido ad ogni step.
