import json
import os

from mcp.server import MCPServer

_CATALOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "catalog.json")

mcp = MCPServer("catalogo")


def _load_catalog(path=_CATALOG_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _search(query, items):
    q = query.lower()
    hits = [it for it in items if q in it["nome"].lower() or q in it["categoria"].lower()]
    if not hits:
        return f"nessuno strumento trovato per '{query}'"
    return "\n".join(f'{it["id"]} — {it["nome"]} ({it["categoria"]})' for it in hits)


def _get(item_id, items):
    for it in items:
        if it["id"] == item_id:
            return (f'{it["id"]} — {it["nome"]}\n'
                    f'categoria: {it["categoria"]}\n'
                    f'descrizione: {it["descrizione"]}\n'
                    f'disponibili: {it["quantita_disponibile"]}')
    return f"strumento non trovato: {item_id}"


@mcp.tool()
def search_catalog(query: str) -> str:
    """Cerca strumenti nel catalogo del laboratorio per nome o categoria (corrispondenza
    per sottostringa, maiuscole/minuscole indifferenti). Passa UN solo termine semplice,
    non una frase: il nome di uno strumento (es. 'oscilloscopio', 'multimetro') oppure una
    categoria (una tra: misura, utensili, alimentazione, componenti, sicurezza). Restituisce
    id, nome e categoria di ogni strumento corrispondente, o un messaggio se non ce ne sono."""
    return _search(query, _load_catalog())


@mcp.tool()
def get_item(item_id: str) -> str:
    """Restituisce il dettaglio completo di uno strumento dato il suo identificativo esatto
    (es. 'MIS-002', 'UTE-010'): nome, categoria, descrizione e quantità disponibile. Usa
    questo strumento quando conosci già l'id; per trovarlo da nome o categoria usa prima
    search_catalog."""
    return _get(item_id, _load_catalog())


if __name__ == "__main__":
    mcp.run(transport="stdio")
