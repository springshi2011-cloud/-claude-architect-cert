from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from exercises import ex01_messages


@pytest.fixture
def captured_request(monkeypatch):
    """Swap in a fake client and hand back the kwargs it was called with."""
    fake = MagicMock()
    fake.messages.create.return_value = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="mocked answer")]
    )
    monkeypatch.setattr(ex01_messages, "get_client", lambda: fake)
    return fake.messages.create


def test_ask_returns_text(captured_request):
    assert ex01_messages.ask("hi") == "mocked answer"


def test_ask_sends_adaptive_thinking_and_no_retired_params(captured_request):
    ex01_messages.ask("hi", effort="high")
    kwargs = captured_request.call_args.kwargs

    assert kwargs["model"] == "claude-opus-4-8"
    assert kwargs["thinking"]["type"] == "adaptive"
    assert kwargs["output_config"] == {"effort": "high"}

    # These all return a 400 on the current model. Guard against regressions.
    assert "budget_tokens" not in kwargs["thinking"]
    for retired in ("temperature", "top_p", "top_k"):
        assert retired not in kwargs

    # A trailing assistant turn (prefill) is also a 400 now.
    assert kwargs["messages"][-1]["role"] == "user"
