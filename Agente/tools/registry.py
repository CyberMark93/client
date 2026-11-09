from tools.local import LOCAL_TOOLS, LOCAL_REGISTRY

# Copie mutabili: le aggiunte MCP (runtime) non toccano i dizionari dei tool locali.
TOOLS = list(LOCAL_TOOLS)
TOOL_REGISTRY = dict(LOCAL_REGISTRY)
