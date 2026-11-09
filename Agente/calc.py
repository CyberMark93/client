import ast
import math

MAX_EXPR_LEN = 500
MAX_RESULT_DIGITS = 1000


class _CalcError(Exception):
    """Rifiuto esplicito: il messaggio è la stringa restituita all'utente."""


# Operatori binari ammessi: tipo-nodo ast -> funzione. Pow è gestito a parte (Task 2).
_BINOPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
}
_UNARYOPS = {
    ast.UAdd: lambda a: +a,
    ast.USub: lambda a: -a,
}


def _eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise _CalcError("operazione non consentita")
        return node.value
    if isinstance(node, ast.BinOp):
        op = _BINOPS.get(type(node.op))
        if op is None:
            raise _CalcError("operazione non consentita")
        return op(_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _UNARYOPS.get(type(node.op))
        if op is None:
            raise _CalcError("operazione non consentita")
        return op(_eval(node.operand))
    raise _CalcError("operazione non consentita")


def _fmt(x):
    if isinstance(x, int):
        return str(x)
    return f"{x:.12g}"


def calculate(expression):
    if len(expression) > MAX_EXPR_LEN:
        return "espressione troppo lunga"
    try:
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError):
        return "espressione non valida"
    try:
        result = _eval(tree.body)
    except _CalcError as e:
        return str(e)
    except ZeroDivisionError:
        return "divisione per zero"
    except (OverflowError, ValueError):
        return "risultato non valido"
    if isinstance(result, float) and not math.isfinite(result):
        return "risultato non valido"
    return f"{expression} = {_fmt(result)}"


CALC_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Valuta un'espressione aritmetica (elenco chiuso: + - * / ** % //, parentesi), senza eval. Errore su input non valido.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "espressione aritmetica, es. 2 + 3 * (4 - 1)"},
            },
            "required": ["expression"],
        },
    },
}
