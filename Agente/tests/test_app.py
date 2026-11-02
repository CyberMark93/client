import app


class FakeGraph:
    def invoke(self, state, config=None):
        return {"messages": state["messages"] + [{"role": "assistant", "content": "risposta"}],
                "steps": 1}


def test_handle_turn_accumula_la_cronologia():
    messages = [{"role": "system", "content": "s"}]
    messages = app.handle_turn(FakeGraph(), messages, "prima")
    messages = app.handle_turn(FakeGraph(), messages, "seconda")
    roles = [m["role"] for m in messages]
    assert roles == ["system", "user", "assistant", "user", "assistant"]
    assert messages[1]["content"] == "prima"
    assert messages[3]["content"] == "seconda"
