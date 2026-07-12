"""Exercise 4 — structured outputs.

`messages.parse()` validates the response against a Pydantic model and hands back
a typed instance. This is the replacement for the old assistant-prefill trick
(prefilling the last assistant turn now returns a 400 on current models).

Run: python -m exercises.ex04_structured
"""

from pydantic import BaseModel

from exercises.config import MODEL, get_client


class Contact(BaseModel):
    name: str
    email: str
    plan: str
    interests: list[str]
    demo_requested: bool


def extract(blurb: str) -> Contact:
    """Pull a structured Contact out of freeform text."""
    client = get_client()
    response = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        messages=[{"role": "user", "content": f"Extract the contact details:\n\n{blurb}"}],
        output_format=Contact,
    )
    return response.parsed_output


if __name__ == "__main__":
    contact = extract(
        "Jane Doe (jane@example.com) is evaluating the Enterprise plan. "
        "She cares about the API and the SDKs, and asked for a demo next week."
    )
    print(contact.model_dump_json(indent=2))
