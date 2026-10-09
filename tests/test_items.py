import pytest

from core.items.item_loader import load_items
from core.items.base import Item, Slot, Attack, Defense

def test_load_items():
    items = load_items()
    assert items, "No items were loaded"
    assert isinstance(items, dict)
    for item_id, item in items.items():
        assert isinstance(item_id, str)
        assert isinstance(item, Item)

def test_wooden_sword_types():
    sword = load_items()["wooden_sword"]
    assert isinstance(sword.attack, Attack)
    assert sword.attack.hits == 1
    assert sword.slots == ((Slot.RIGHT_HAND,), (Slot.LEFT_HAND,))