import pytest

from core.items.base import Item, ItemInstance, Slot
from core.items.catalog import ItemCatalog, UnknownItem


@pytest.fixture
def catalog() -> ItemCatalog:
    return ItemCatalog({
        "potion": Item(id="potion", max_stack=10, category="consumables"),
        "sword": Item(id="sword", category="weapons", slots=((Slot.RIGHT_HAND,), (Slot.LEFT_HAND,))),
    })


def test_get_returns_definition(catalog):
    assert catalog.get("sword").id == "sword"


def test_get_unknown_raises(catalog):
    with pytest.raises(UnknownItem):
        catalog.get("ghost")


def test_contains(catalog):
    assert "potion" in catalog
    assert "ghost" not in catalog


def test_by_category(catalog):
    assert [i.id for i in catalog.by_category("weapons")] == ["sword"]
    assert catalog.categories() == ["consumables", "weapons"]


def test_create_stackable_has_no_state(catalog):
    assert catalog.create("potion") == ItemInstance("potion")


def test_create_equippable_starts_with_full_wear(catalog):
    assert catalog.create("sword") == ItemInstance("sword", wear=1.0)
