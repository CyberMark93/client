import graph


def test_grafo_a_risposta_fissa_appende_assistant_e_incrementa_steps():
    g = graph.build_graph(lambda messages, tools: {"role": "assistant", "content": "ciao fisso"})
    out = g.invoke({"messages": [{"role": "user", "content": "x"}], "steps": 0})
    assert out["messages"][-1] == {"role": "assistant", "content": "ciao fisso"}
    assert len(out["messages"]) == 2
    assert out["steps"] == 1
