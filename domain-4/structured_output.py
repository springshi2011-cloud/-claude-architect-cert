"""Domain 4 — structured extraction via tool_use, with a validation-retry loop.

Claude is given a tool, `record_book`, that captures exactly three fields — title,
author, and year. We force the tool with `tool_choice`, then validate the arguments
Claude produced against a Pydantic model *on our side*. If validation fails (e.g. the
year is missing or implausible), we feed the error back as a `tool_result` with
`is_error=True` and let Claude try again. That client-side loop is the point of the
exercise: the model proposes structured arguments, we verify them, and we only accept
input that actually satisfies the schema.

Why tool_use instead of `messages.parse()`? `messages.parse()` (see ex04_structured)
validates once and raises on failure. Here we want to *recover* from a bad extraction
by handing the validation error back to the model — the tool loop makes that natural.

API constraints this repo is built around (do not reintroduce):
  - model is pinned to claude-opus-4-8
  - no temperature / top_p / top_k — steer with prompting
  - no assistant-turn prefill

Run: python domain-4/structured_output.py   (needs ANTHROPIC_API_KEY)
"""

from __future__ import annotations

import anthropic
from pydantic import BaseModel, Field, ValidationError

# Pinned in one place, mirroring src/exercises/config.py. This folder lives outside
# the `exercises` package, so the constant is inlined rather than imported.
MODEL = "claude-opus-4-8"
MAX_ATTEMPTS = 3

# The current year bounds the plausible-range check below. Update alongside the repo.
CURRENT_YEAR = 2026


class Book(BaseModel):
    """The exact shape we require back. Extra keys are rejected."""

    model_config = {"extra": "forbid"}

    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    # ge/le turn an out-of-range or missing year into a ValidationError we can hand back.
    year: int = Field(ge=1400, le=CURRENT_YEAR)


# Tool definition. `year` is listed as required so the intent is explicit, but the tool
# is deliberately NOT strict — that lets Claude omit the year when the text doesn't state
# one, so our own Pydantic pass is what drives the retry rather than a hard API error.
RECORD_BOOK_TOOL: anthropic.types.ToolParam = {
    "name": "record_book",
    "description": "Record the three bibliographic fields extracted from a passage.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "The book's title."},
            "author": {"type": "string", "description": "The author's full name."},
            "year": {
                "type": "integer",
                "description": "Four-digit year the book was first published.",
            },
        },
        "required": ["title", "author", "year"],
    },
}


def _tool_use_block(message: anthropic.types.Message) -> anthropic.types.ToolUseBlock:
    """Pull the record_book call out of a response; content is a list of blocks."""
    for block in message.content:
        if block.type == "tool_use" and block.name == "record_book":
            return block
    raise RuntimeError("model did not call record_book")


def extract_book(text: str) -> Book:
    """Extract a validated Book from free text, retrying on validation failure.

    The first turn tells Claude to only record a year that is *explicitly stated*, so a
    passage with no date fails validation and exercises the retry path. The error we feed
    back then relaxes that instruction to a best estimate.
    """
    client = anthropic.Anthropic()
    messages: list[anthropic.types.MessageParam] = [
        {
            "role": "user",
            "content": (
                "Extract the book's metadata using the record_book tool. "
                "Only record a year that is explicitly stated in the passage.\n\n"
                f"Passage:\n{text}"
            ),
        }
    ]

    for attempt in range(1, MAX_ATTEMPTS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=[RECORD_BOOK_TOOL],
            tool_choice={"type": "tool", "name": "record_book"},
            messages=messages,
        )
        tool_use = _tool_use_block(response)
        print(f"  attempt {attempt}: model proposed {tool_use.input}")

        try:
            book = Book.model_validate(tool_use.input)
            print(f"  attempt {attempt}: valid ✓")
            return book
        except ValidationError as exc:
            # Report which fields failed so the feedback is specific and actionable.
            problems = "; ".join(
                f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()
            )
            print(f"  attempt {attempt}: rejected — {problems}")

            # Carry the failed call forward, then answer it with an error tool_result.
            # Preserving response.content keeps the tool_use block Claude must respond to.
            messages.append({"role": "assistant", "content": response.content})
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "is_error": True,
                            "content": (
                                f"Validation failed: {problems}. "
                                "The year is required. If the passage does not state one, "
                                "supply your best-known estimate of the publication year "
                                "and call record_book again."
                            ),
                        }
                    ],
                }
            )

    raise RuntimeError(f"could not extract a valid book in {MAX_ATTEMPTS} attempts")


if __name__ == "__main__":
    good = (
        "The Great Gatsby is a 1925 novel by the American writer "
        "F. Scott Fitzgerald."
    )
    # Same book, but the year is deliberately absent — the first extraction can't
    # satisfy the schema, so the retry loop kicks in and Claude estimates on turn two.
    missing_year = "The Great Gatsby is a novel by the American writer F. Scott Fitzgerald."

    print("== Clean passage (validates on the first attempt) ==")
    book = extract_book(good)
    print(f"  -> {book.model_dump_json()}\n")

    print("== Passage missing the year (validation-retry loop) ==")
    book = extract_book(missing_year)
    print(f"  -> {book.model_dump_json()}")
