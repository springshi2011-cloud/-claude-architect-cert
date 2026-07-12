"""Shared client and request defaults for every exercise.

Exercises import from here rather than constructing their own client so that the
model, thinking mode, and effort are pinned in exactly one place.
"""

from typing import Any

import anthropic

# Current flagship model. Adaptive thinking and effort replace the retired
# `budget_tokens` knob; on this model a request with no `thinking` field runs
# with thinking OFF, so it must be set explicitly to enable it.
MODEL = "claude-opus-4-8"

ADAPTIVE_THINKING: dict[str, Any] = {"type": "adaptive"}

# `display: "summarized"` opts back into readable reasoning text. The default is
# "omitted", which streams thinking blocks whose text is an empty string.
VISIBLE_THINKING: dict[str, Any] = {"type": "adaptive", "display": "summarized"}


def get_client() -> anthropic.Anthropic:
    """Build a client from the ambient credentials.

    Resolves ANTHROPIC_API_KEY, then ANTHROPIC_AUTH_TOKEN, then an `ant auth
    login` profile. Never hardcode a key here.
    """
    return anthropic.Anthropic()


def text_of(message: anthropic.types.Message) -> str:
    """Concatenate the text blocks of a response.

    `message.content` is a list of blocks that may include thinking and tool_use
    alongside text, so indexing `content[0].text` is not safe.
    """
    return "".join(block.text for block in message.content if block.type == "text")
