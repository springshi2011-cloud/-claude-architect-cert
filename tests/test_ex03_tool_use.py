import pytest

from exercises import ex03_tool_use as ex03
from exercises.ex03_tool_use import check_stock, restock


@pytest.fixture(autouse=True)
def fresh_inventory(monkeypatch):
    """Each test gets its own inventory; restock() mutates module state."""
    monkeypatch.setattr(ex03, "_INVENTORY", {"widget": 42, "doohickey": 0})


def test_check_stock_reports_quantity():
    assert "42 units of widget" in check_stock("widget")


def test_check_stock_rejects_unknown_item():
    assert "No product named" in check_stock("nonexistent")


def test_restock_increases_quantity():
    assert "25 units" in restock("doohickey", 25)
    assert "25 units of doohickey" in check_stock("doohickey")


def test_restock_rejects_nonpositive_quantity():
    assert restock("widget", 0) == "Quantity must be positive."
    assert "42 units of widget" in check_stock("widget")


def test_restock_rejects_unknown_item():
    assert "Cannot restock" in restock("nonexistent", 5)


def test_schema_is_derived_from_signature():
    # The decorator, not us, writes the JSON schema the model sees.
    assert restock.name == "restock"
    schema = restock.input_schema
    assert set(schema["required"]) == {"item", "quantity"}
    assert schema["properties"]["quantity"]["type"] == "integer"
    assert "Add units of an item to inventory." in restock.description
