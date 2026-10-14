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

def test_heal_potion_has_on_use_effect():
    potion = load_items()["heal_potion"]
    assert potion.category == "consumables"
    assert potion.usable
    assert potion.on_use == (Effect(type="heal", value=5),)
    assert not potion.equippable


def test_item_without_effects_is_not_usable():
    assert not load_items()["wooden_sword"].usable


def test_effect_rejects_non_positive_value():
    with pytest.raises(ValueError):
        Effect(type="heal", value=0)
