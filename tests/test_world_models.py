import dataclasses

import pytest

from core.enums import Direction
from core.world.models import Room, RoomRef, World, Zone


# --- Données de test --------------------------------------------------------

@pytest.fixture
def small_world() -> World:
    """Deux zones reliées : village (place <-> porte) et grotte (entrée)."""
    square_ref = RoomRef("village", "square")
    gate_ref = RoomRef("village", "gate")
    cave_ref = RoomRef("cave", "entrance")

    village = Zone(
        id="village",
        name="Village",
        description="Un petit village.",
        entry_room="square",
        rooms={
            "square": Room("Place", "La place du village.", square_ref,
                           exits={Direction.SOUTH: gate_ref}),
            "gate": Room("Porte", "La porte du village.", gate_ref,
                         exits={Direction.NORTH: square_ref,
                                Direction.SOUTH: cave_ref}),
        },
    )
    cave = Zone(
        id="cave",
        name="Grotte",
        description="Une grotte humide.",
        entry_room="entrance",
        rooms={
            "entrance": Room("Entrée", "L'entrée de la grotte.", cave_ref,
                             exits={Direction.NORTH: gate_ref}),
        },
    )
    return World(start=square_ref, zones={"village": village, "cave": cave})


# --- RoomRef ----------------------------------------------------------------

def test_room_refs_with_same_ids_are_equal():
    assert RoomRef("village", "square") == RoomRef("village", "square")


def test_room_refs_with_different_ids_are_not_equal():
    assert RoomRef("village", "square") != RoomRef("village", "gate")
    assert RoomRef("village", "square") != RoomRef("cave", "square")


def test_room_ref_is_hashable():
    # Indispensable pour s'en servir comme clé de dict ou dans un set.
    refs = {RoomRef("village", "square"), RoomRef("village", "square")}
    assert len(refs) == 1


def test_room_ref_is_immutable():
    ref = RoomRef("village", "square")
    with pytest.raises(dataclasses.FrozenInstanceError):
        ref.room = "gate"


# --- Room -------------------------------------------------------------------

def test_room_defaults():
    room = Room("Place", "La place.", RoomRef("village", "square"))
    assert room.look_around == ""
    assert room.exits == {}


def test_rooms_do_not_share_default_exits():
    a = Room("A", "", RoomRef("z", "a"))
    b = Room("B", "", RoomRef("z", "b"))
    assert a.exits is not b.exits


def test_room_is_immutable():
    room = Room("Place", "La place.", RoomRef("village", "square"))
    with pytest.raises(dataclasses.FrozenInstanceError):
        room.name = "Autre"


def test_missing_exit_is_absent_key():
    room = Room("Place", "", RoomRef("z", "a"),
                exits={Direction.NORTH: RoomRef("z", "b")})
    assert Direction.NORTH in room.exits
    assert Direction.SOUTH not in room.exits


# --- World.get_room ---------------------------------------------------------

def test_get_room_returns_the_right_room(small_world):
    room = small_world.get_room(RoomRef("village", "gate"))
    assert room.name == "Porte"
    assert room.ref == RoomRef("village", "gate")


def test_get_room_across_zones(small_world):
    room = small_world.get_room(RoomRef("cave", "entrance"))
    assert room.ref.zone_id == "cave"


def test_start_room_exists(small_world):
    assert small_world.get_room(small_world.start).ref == small_world.start


def test_exits_lead_to_existing_rooms(small_world):
    for zone in small_world.zones.values():
        for room in zone.rooms.values():
            for target in room.exits.values():
                small_world.get_room(target)   # ne doit pas lever


def test_get_room_unknown_zone_raises(small_world):
    with pytest.raises(ValueError, match="nowhere"):
        small_world.get_room(RoomRef("nowhere", "square"))


def test_get_room_unknown_room_raises(small_world):
    with pytest.raises(ValueError, match="attic"):
        small_world.get_room(RoomRef("village", "attic"))