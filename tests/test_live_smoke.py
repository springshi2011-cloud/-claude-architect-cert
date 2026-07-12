"""Smoke tests that hit the real API.

Deselected by default (see `addopts` in pyproject.toml). Run them with:

    pytest -m live
"""

import os

import pytest

from exercises import ex01_messages, ex04_structured

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY is not set",
    ),
]


def test_basic_message_round_trip():
    answer = ex01_messages.ask("Reply with exactly the word: pong", effort="low")
    assert "pong" in answer.lower()


def test_structured_extraction_round_trip():
    contact = ex04_structured.extract(
        "Ada Lovelace (ada@example.com) wants the Pro plan and asked for a demo. "
        "She's interested in analytics."
    )
    assert contact.email == "ada@example.com"
    assert contact.demo_requested is True
