"""Exercise 3 — tool use via the SDK tool runner.

`@beta_tool` derives the JSON schema from the signature and docstring, and
`tool_runner` drives the call -> execute -> feed-result-back loop, so there is no
hand-written `while stop_reason == "tool_use"` loop here.

Run: python -m exercises.ex03_tool_use
"""

from anthropic import beta_tool

from exercises.config import MODEL, get_client, text_of

# Stand-in for a real data source, so the exercise runs offline-ish.
_INVENTORY = {"widget": 42, "gizmo": 7, "doohickey": 0}


@beta_tool
def check_stock(item: str) -> str:
    """Look up how many units of an item are in stock.

    Args:
        item: The product name, e.g. "widget".
    """
    if item not in _INVENTORY:
        return f"No product named {item!r} exists."
    return f"{_INVENTORY[item]} units of {item} in stock."


@beta_tool
def restock(item: str, quantity: int) -> str:
    """Add units of an item to inventory.

    Args:
        item: The product name.
        quantity: How many units to add. Must be positive.
    """
    if item not in _INVENTORY:
        return f"Cannot restock unknown product {item!r}."
    if quantity <= 0:
        return "Quantity must be positive."
    _INVENTORY[item] += quantity
    return f"Restocked {item}; now {_INVENTORY[item]} units."


def run(prompt: str) -> str:
    """Let Claude call the inventory tools until it has an answer."""
    client = get_client()
    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=16000,
        tools=[check_stock, restock],
        messages=[{"role": "user", "content": prompt}],
    )

    last = None
    for message in runner:
        last = message
    return text_of(last) if last else ""


if __name__ == "__main__":
    print(run("We're out of doohickeys. Check, then bring them up to 25 units."))
