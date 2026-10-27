import operator
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    messages: Annotated[list, operator.add]
    steps: int


def make_call_model(llm_fn, tools=None):
    def call_model(state):
        assistant = llm_fn(state["messages"], tools)
        return {"messages": [assistant], "steps": state["steps"] + 1}
    return call_model


def build_graph(llm_fn, tools=None):
    builder = StateGraph(State)
    builder.add_node("call_model", make_call_model(llm_fn, tools))
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", END)
    return builder.compile()
