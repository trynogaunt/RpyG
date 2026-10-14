import pytest

from core.items.item_loader import load_items
from core.items.base import Item, Slot, Attack, Defense, Effect

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

def test_loader_sets_category_from_folder():
    items = load_items()
    assert items["wooden_sword"].category == "weapons"
    assert items["wooden_shield"].category == "shields"

@pytest.mark.parametrize("item_id", ["heal_potion", "medicinal_herb"])
def test_healing_consumables_have_on_use_effect(item_id):
    item = load_items()[item_id]
    assert item.category == "consumables"
    assert item.usable
    assert [e.type for e in item.on_use] == ["heal"]
    assert all(isinstance(e, Effect) and e.value > 0 for e in item.on_use)
    assert not item.equippable


def test_item_without_effects_is_not_usable():
    assert not load_items()["wooden_sword"].usable


def test_effect_rejects_non_positive_value():
    with pytest.raises(ValueError):
        Effect(type="heal", value=0)
