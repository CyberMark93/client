import os
import sys

from dotenv import load_dotenv


def load_config(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.isfile(path):
        sys.exit(f"File di configurazione non trovato: {path}. Copia .env.example in .env e compilalo.")
    load_dotenv(path, override=False)
    base_url = os.environ.get("LM_BASE_URL")
    model = os.environ.get("LM_MODEL")
    missing = [k for k, v in (("LM_BASE_URL", base_url), ("LM_MODEL", model)) if not v]
    if missing:
        sys.exit(f"Config mancante: {', '.join(missing)}. Compila il file .env.")
    return base_url.rstrip("/"), model
