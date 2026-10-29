import requests


def call_llm(base_url, model, messages, tools=None, max_tokens=1024, temperature=0.2):
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    try:
        resp = requests.post(f"{base_url}/chat/completions", json=payload, timeout=(5, 120))
    except requests.exceptions.Timeout:
        raise SystemExit("Attesa scaduta: controllare server, carico e tempi.")
    except requests.exceptions.ConnectionError:
        raise SystemExit(
            f"Connessione fallita su {base_url}: controllare server, URL e porta. "
            "Avvialo con: lms server start"
        )
    if resp.status_code != 200:
        raise SystemExit(f"Errore HTTP: {resp.status_code} {resp.text}")
    return resp.json()["choices"][0]["message"]
