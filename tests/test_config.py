from types import SimpleNamespace

from exercises.config import ADAPTIVE_THINKING, MODEL, VISIBLE_THINKING, text_of


def test_model_is_current_flagship():
    assert MODEL == "claude-opus-4-8"


def test_thinking_uses_adaptive_not_retired_budget_tokens():
    # budget_tokens is removed on this model and returns a 400 if sent.
    assert ADAPTIVE_THINKING == {"type": "adaptive"}
    assert "budget_tokens" not in VISIBLE_THINKING
    assert VISIBLE_THINKING["display"] == "summarized"


def test_text_of_skips_non_text_blocks():
    message = SimpleNamespace(
        content=[
            SimpleNamespace(type="thinking", thinking="reasoning..."),
            SimpleNamespace(type="text", text="Hello "),
            SimpleNamespace(type="text", text="world."),
        ]
    )
    assert text_of(message) == "Hello world."


def test_text_of_returns_empty_when_no_text_blocks():
    message = SimpleNamespace(content=[SimpleNamespace(type="tool_use", name="x")])
    assert text_of(message) == ""
