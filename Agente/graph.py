import json
import logging
import operator
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END

from tools import TOOL_REGISTRY

logger = logging.getLogger(__name__)
MAX_STEPS = 3


class State(TypedDict):
    messages: Annotated[list, operator.add]
    steps: int


def make_call_model(llm_fn, tools=None):
    def call_model(state):
        assistant = llm_fn(state["messages"], tools)
        return {"messages": [assistant], "steps": state["steps"] + 1}
    return call_model


def should_continue(state):
    last = state["messages"][-1]
    if last.get("tool_calls") and state["steps"] < MAX_STEPS:
        return "tools"
    return END


def tools_node(state):
    last = state["messages"][-1]
    out = []
    for call in last["tool_calls"]:
        name = call["function"]["name"]
        args = json.loads(call["function"]["arguments"])
        logger.info("tool-call %s(%s)", name, args)
        result = TOOL_REGISTRY[name](**args)
        logger.info("tool-result %s -> %s", name, result)
        out.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    return {"messages": out}


def build_graph(llm_fn, tools=None):
    builder = StateGraph(State)
    builder.add_node("call_model", make_call_model(llm_fn, tools))
    builder.add_edge(START, "call_model")
    if tools:
        builder.add_node("tools", tools_node)
        builder.add_conditional_edges("call_model", should_continue, {"tools": "tools", END: END})
        builder.add_edge("tools", "call_model")
    else:
        builder.add_edge("call_model", END)
    return builder.compile()
