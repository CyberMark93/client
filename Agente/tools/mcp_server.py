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
    """Cerca strumenti di laboratorio per nome o categoria."""
    return _search(query, _load_catalog())


@mcp.tool()
def get_item(item_id: str) -> str:
    """Restituisce il dettaglio di uno strumento di laboratorio dato il suo id."""
    return _get(item_id, _load_catalog())


if __name__ == "__main__":
    mcp.run(transport="stdio")
