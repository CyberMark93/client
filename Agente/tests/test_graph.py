import json

from langgraph.graph import END

import graph
import graph as graph_mod


def test_grafo_a_risposta_fissa_appende_assistant_e_incrementa_steps():
    g = graph.build_graph(lambda messages, tools: {"role": "assistant", "content": "ciao fisso"})
    out = g.invoke({"messages": [{"role": "user", "content": "x"}], "steps": 0})
    assert out["messages"][-1] == {"role": "assistant", "content": "ciao fisso"}
    assert len(out["messages"]) == 2
    assert out["steps"] == 1


def _tool_call(tz):
    return {
        "role": "assistant",
        "content": "",
        "tool_calls": [{"id": "c1", "type": "function",
                        "function": {"name": "get_current_time",
                                     "arguments": json.dumps({"timezone": tz})}}],
    }


def test_instradamento_esegue_il_tool_e_poi_risponde():
    risposte = [_tool_call("Europe/Rome"), {"role": "assistant", "content": "Sono le 12."}]

    def fake_llm(messages, tools):
        return risposte.pop(0)

    g = graph_mod.build_graph(fake_llm, tools=[{"x": 1}])
    out = g.invoke({"messages": [{"role": "user", "content": "che ora e'?"}], "steps": 0})
    roles = [m["role"] for m in out["messages"]]
    assert roles == ["user", "assistant", "tool", "assistant"]
    assert "(Europe/Rome)" in out["messages"][2]["content"]
    assert out["messages"][-1]["content"] == "Sono le 12."


def test_limite_passi_ferma_il_ciclo():
    def fake_llm_sempre_tool(messages, tools):
        return _tool_call("Europe/Rome")

    g = graph_mod.build_graph(fake_llm_sempre_tool, tools=[{"x": 1}])
    out = g.invoke({"messages": [{"role": "user", "content": "loop"}], "steps": 0},
                   config={"recursion_limit": 50})
    assert out["steps"] == graph_mod.MAX_STEPS


def test_should_continue_va_a_END_senza_tool_calls():
    state = {"messages": [{"role": "assistant", "content": "finito"}], "steps": 1}
    assert graph_mod.should_continue(state) == END
