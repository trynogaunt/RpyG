import pytest

from core.items.base import Item
from core.game.inventory import Inventory

@pytest.fixture
def potion() -> Item:
    return Item(id="potion", max_stack=10)


@pytest.fixture
def sword() -> Item:
    return Item(id="sword", max_stack=1)


@pytest.fixture
def bag() -> Inventory:
    return Inventory(size=2)


def contents(inv: Inventory) -> list[tuple[str | None, int]]:
    """Vue simplifiée du sac pour comparer facilement."""
    return [(c.item_id, c.quantity) for c in inv.cases]


def test_add_splits_over_several_cases(bag, potion):
    assert bag.add(potion, 15) == 0
    assert contents(bag) == [("potion", 10), ("potion", 5)]


def test_add_completes_existing_stack_first(bag, potion):
    bag.add(potion, 15)
    assert bag.add(potion, 3) == 0
    assert contents(bag) == [("potion", 10), ("potion", 8)]


def test_add_fills_stack_then_opens_new_case(bag, potion):
    bag.add(potion, 7)
    assert bag.add(potion, 6) == 0
    assert contents(bag) == [("potion", 10), ("potion", 3)]


def test_add_returns_remainder_when_bag_is_full(bag, potion):
    assert bag.add(potion, 25) == 5
    assert contents(bag) == [("potion", 10), ("potion", 10)]


def test_non_stackable_items_take_one_case_each(bag, sword):
    assert bag.add(sword, 3) == 1
    assert contents(bag) == [("sword", 1), ("sword", 1)]


def test_full_bag_adds_nothing(bag, sword, potion):
    bag.add(sword, 2)
    assert bag.add(potion, 5) == 5
    assert contents(bag) == [("sword", 1), ("sword", 1)]


def test_different_items_do_not_merge(bag, potion):
    other = Item(id="elixir", max_stack=10)
    bag.add(potion, 4)
    bag.add(other, 4)
    assert contents(bag) == [("potion", 4), ("elixir", 4)]


@pytest.mark.parametrize("quantity", [0, -1])
def test_invalid_quantity_raises_and_changes_nothing(bag, potion, quantity):
    with pytest.raises(ValueError):
        bag.add(potion, quantity)
    assert contents(bag) == [(None, 0), (None, 0)]

@pytest.fixture
def bag3() -> Inventory:
    return Inventory(size=3)


def test_remove_part_of_a_stack(bag, potion):
    bag.add(potion, 8)
    assert bag.remove(potion, 3) == 0
    assert contents(bag) == [("potion", 5), (None, 0)]


def test_remove_whole_stack_empties_the_case(bag, potion):
    bag.add(potion, 8)
    assert bag.remove(potion, 8) == 0
    assert contents(bag) == [(None, 0), (None, 0)]
    assert all(c.is_empty for c in bag.cases)


def test_remove_across_several_stacks(bag, potion):
    bag.add(potion, 15)
    assert bag.remove(potion, 12) == 0
    assert contents(bag) == [("potion", 3), (None, 0)]


def test_remove_takes_last_stack_first(bag, potion):
    bag.add(potion, 15)               # (potion, 10), (potion, 5)
    bag.remove(potion, 7)
    assert contents(bag) == [("potion", 8), (None, 0)]


def test_remove_more_than_owned_returns_missing(bag, potion):
    bag.add(potion, 4)
    assert bag.remove(potion, 10) == 6
    assert contents(bag) == [(None, 0), (None, 0)]


def test_remove_item_not_in_bag_changes_nothing(bag, potion, sword):
    bag.add(sword, 1)
    assert bag.remove(potion, 3) == 3
    assert contents(bag) == [("sword", 1), (None, 0)]


def test_remove_only_touches_the_requested_item(bag3, potion, sword):
    bag3.add(potion, 5)
    bag3.add(sword, 1)
    bag3.remove(potion, 5)
    assert contents(bag3) == [(None, 0), ("sword", 1), (None, 0)]


def test_removed_case_can_be_reused(bag, potion, sword):
    bag.add(potion, 2)
    bag.remove(potion, 2)
    assert bag.add(sword, 1) == 0
    assert contents(bag) == [("sword", 1), (None, 0)]


@pytest.mark.parametrize("quantity", [0, -1])
def test_remove_invalid_quantity_raises(bag, potion, quantity):
    bag.add(potion, 5)
    with pytest.raises(ValueError):
        bag.remove(potion, quantity)
    assert contents(bag) == [("potion", 5), (None, 0)]