import pytest

from core.enums import Direction
from core.world.models import RoomRef

SQUARE = RoomRef("village", "square")
GATE = RoomRef("village", "gate")
ENTRANCE = RoomRef("cave", "entrance")


def test_exit_from_returns_target(small_world):
    assert small_world.exit_from(SQUARE, Direction.SOUTH) == GATE


def test_exit_from_without_exit_returns_none(small_world):
    assert small_world.exit_from(SQUARE, Direction.NORTH) is None


def test_exit_from_to_another_zone(small_world):
    assert small_world.exit_from(GATE, Direction.SOUTH) == ENTRANCE


def test_exit_from_back_from_another_zone(small_world):
    assert small_world.exit_from(ENTRANCE, Direction.NORTH) == GATE


def test_exit_from_unknown_room_raises(small_world):
    with pytest.raises(ValueError):
        small_world.exit_from(RoomRef("village", "attic"), Direction.NORTH)


@pytest.mark.parametrize("direction", list(Direction))
def test_exit_from_always_returns_ref_or_none(small_world, direction):
    target = small_world.exit_from(SQUARE, direction)
    assert target is None or isinstance(target, RoomRef)


def test_exit_from_does_not_change_the_world(small_world):
    before = small_world.get_room(SQUARE)
    small_world.exit_from(SQUARE, Direction.SOUTH)
    assert small_world.get_room(SQUARE) == before