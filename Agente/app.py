import logging

from config import load_config
from llm import call_llm
from graph import build_graph
from tools import CLOCK_TOOLS

SYSTEM_PROMPT = "Rispondi in italiano. Usa lo strumento orologio quando l'utente chiede l'ora o la data."
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
    graph = build_graph(llm_fn, tools=CLOCK_TOOLS)
    run_chat(graph)


if __name__ == "__main__":
    main()
