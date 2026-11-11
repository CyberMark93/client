import logging

from config import load_config
from llm import call_llm
from graph import build_graph
from tools import TOOLS, TOOL_REGISTRY
from tools.mcp_client import discover_mcp_tools
from tools.notes_client import discover_notes_tool

SYSTEM_PROMPT = (
    "Rispondi in italiano. Usa lo strumento orologio quando l'utente chiede l'ora o la data. "
    "Usa lo strumento di conversione quando l'utente chiede di convertire un valore tra unità di misura. "
    "Usa la calcolatrice quando l'utente chiede di calcolare un'espressione aritmetica. "
    "Usa lo strumento date per giorni della settimana, differenze tra date, giorni lavorativi e scadenze. "
    "Usa il catalogo (search_catalog, get_item) quando l'utente cerca strumenti di laboratorio o chiede il dettaglio di uno strumento. "
    "Usa lo strumento note per aggiungere, elencare, modificare o eliminare note personali; per eliminare, conferma con conferma=true."
)
EXIT_WORD = "esci"


def handle_turn(graph, messages, text):
    messages = messages + [{"role": "user", "content": text}]
    state = graph.invoke({"messages": messages, "steps": 0}, config={"recursion_limit": 10})
    return state["messages"]


def run_chat(graph, system_prompt=SYSTEM_PROMPT):
    messages = [{"role": "system", "content": system_prompt}]
    print(f"Chat avviata. Scrivi '{EXIT_WORD}' o premi Ctrl+C per uscire.")
    while True:
        try:
            text = input("Tu> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text.lower() == EXIT_WORD:
            break
        messages = handle_turn(graph, messages, text)
        print("Assistente>", messages[-1].get("content", ""))


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    base_url, model = load_config()
    llm_fn = lambda msgs, tools: call_llm(base_url, model, msgs, tools)
    all_tools = TOOLS
    try:
        mcp_schemas, mcp_registry = discover_mcp_tools()
        TOOL_REGISTRY.update(mcp_registry)
        all_tools = TOOLS + mcp_schemas
    except Exception as exc:  # degradazione: l'app parte coi soli tool locali
        logging.getLogger(__name__).warning("discovery MCP fallita: %s", exc)
    try:
        notes_schemas, notes_registry = discover_notes_tool()
        TOOL_REGISTRY.update(notes_registry)
        all_tools = all_tools + notes_schemas
    except Exception as exc:  # l'app parte comunque, senza il tool note
        logging.getLogger(__name__).warning("discovery note fallita: %s", exc)
    graph = build_graph(llm_fn, tools=all_tools)
    run_chat(graph)


if __name__ == "__main__":
    main()
