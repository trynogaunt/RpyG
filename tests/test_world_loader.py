import json
from pathlib import Path

import pytest

from core.enums import Direction
from core.world.loader import load_world
from core.world.models import RoomRef, World


# --- Construction de mondes de test ------------------------------------------

def base_world() -> dict:
    """Un petit monde valide : un village (place <-> porte) et une grotte (entrée <-> bassin)."""
    return {
        "world": {
            "start": {"zone": "village", "room": "square"},
            "zones": ["village", "cave"],
        },
        "zones": {
            "village": {
                "id": "village",
                "name": "Village",
                "description": "Un petit village.",
                "entry_room": "square",
                "rooms": {
                    "square": {
                        "name": "Place",
                        "description": "La place du village.",
                        "look_around": "Des enfants jouent.",
                        "exits": {"south": {"room": "gate"}},
                    },
                    "gate": {
                        "name": "Porte",
                        "description": "La porte du village.",
                        "exits": {
                            "north": {"room": "square"},
                            "south": {"zone": "cave"},
                        },
                    },
                },
            },
            "cave": {
                "id": "cave",
                "name": "Grotte",
                "description": "Une grotte humide.",
                "entry_room": "entrance",
                "rooms": {
                    "entrance": {
                        "name": "Entrée",
                        "description": "L'entrée de la grotte.",
                        "exits": {
                            "north": {"zone": "village", "room": "gate"},
                            "south": {"room": "pool"},
                        },
                    },
                    "pool": {
                        "name": "Bassin",
                        "description": "Un bassin d'eau froide.",
                        "exits": {"north": {"room": "entrance"}},
                    },
                },
            },
        },
    }


def write_world(directory: Path, data: dict) -> Path:
    """Écrit world.json et zones/*.json dans `directory`, renvoie le dossier."""
    (directory / "zones").mkdir(parents=True, exist_ok=True)
    (directory / "world.json").write_text(json.dumps(data["world"]), encoding="utf-8")
    for zone_id, zone in data["zones"].items():
        (directory / "zones" / f"{zone_id}.json").write_text(json.dumps(zone), encoding="utf-8")
    return directory


@pytest.fixture
def world_data() -> dict:
    return base_world()


@pytest.fixture
def world(tmp_path, world_data) -> World:
    return load_world(write_world(tmp_path, world_data))


# --- Chargement d'un monde valide ------------------------------------------------

def test_returns_a_world(world):
    assert isinstance(world, World)


def test_loads_all_zones(world):
    assert set(world.zones) == {"village", "cave"}


def test_loads_all_rooms(world):
    assert set(world.zones["village"].rooms) == {"square", "gate"}
    assert set(world.zones["cave"].rooms) == {"entrance", "pool"}


def test_start_is_read_from_manifest(world):
    assert world.start == RoomRef("village", "square")
    assert world.get_room(world.start).name == "Place"


def test_room_fields(world):
    room = world.get_room(RoomRef("village", "square"))
    assert room.name == "Place"
    assert room.description == "La place du village."
    assert room.look_around == "Des enfants jouent."
    assert room.ref == RoomRef("village", "square")


def test_look_around_is_optional(world):
    assert world.get_room(RoomRef("village", "gate")).look_around == ""


def test_exits_are_optional(tmp_path, world_data):
    del world_data["zones"]["cave"]["rooms"]["pool"]["exits"]
    world = load_world(write_world(tmp_path, world_data))
    assert world.get_room(RoomRef("cave", "pool")).exits == {}


def test_zone_fields(world):
    zone = world.zones["cave"]
    assert zone.id == "cave"
    assert zone.name == "Grotte"
    assert zone.entry_room == "entrance"


def test_accepts_str_path(tmp_path, world_data):
    write_world(tmp_path, world_data)
    assert isinstance(load_world(str(tmp_path)), World)


# --- Conversion des sorties ------------------------------------------------------

def test_exit_keys_are_directions(world):
    exits = world.get_room(RoomRef("village", "gate")).exits
    assert all(isinstance(direction, Direction) for direction in exits)


def test_exit_same_zone(world):
    exits = world.get_room(RoomRef("village", "square")).exits
    assert exits[Direction.SOUTH] == RoomRef("village", "gate")


def test_exit_to_zone_uses_its_entry(world):
    exits = world.get_room(RoomRef("village", "gate")).exits
    assert exits[Direction.SOUTH] == RoomRef("cave", "entrance")


def test_exit_to_zone_and_room(world):
    exits = world.get_room(RoomRef("cave", "entrance")).exits
    assert exits[Direction.NORTH] == RoomRef("village", "gate")


def test_exit_to_zone_follows_entry_room_change(tmp_path, world_data):
    # Changer l'entrée de la grotte doit suffire à rediriger la sortie {"zone": "cave"}
    world_data["zones"]["cave"]["entry_room"] = "pool"
    world = load_world(write_world(tmp_path, world_data))
    exits = world.get_room(RoomRef("village", "gate")).exits
    assert exits[Direction.SOUTH] == RoomRef("cave", "pool")


def test_missing_direction_means_no_exit(world):
    exits = world.get_room(RoomRef("village", "square")).exits
    assert Direction.NORTH not in exits


def test_all_exits_lead_to_existing_rooms(world):
    for zone in world.zones.values():
        for room in zone.rooms.values():
            for target in room.exits.values():
                world.get_room(target)   # ne doit pas lever


def test_unknown_direction_raises(tmp_path, world_data):
    world_data["zones"]["village"]["rooms"]["square"]["exits"] = {"nroth": {"room": "gate"}}
    with pytest.raises(ValueError, match="nroth"):
        load_world(write_world(tmp_path, world_data))


def test_exit_to_unknown_zone_raises(tmp_path, world_data):
    world_data["zones"]["village"]["rooms"]["gate"]["exits"]["south"] = {"zone": "forest"}
    with pytest.raises(ValueError, match="forest"):
        load_world(write_world(tmp_path, world_data))


def test_missing_zone_file_raises(tmp_path, world_data):
    world_data["world"]["zones"].append("forest")
    with pytest.raises(FileNotFoundError):
        load_world(write_world(tmp_path, world_data))


# --- Validation (à faire passer avec validate_world) ----------------------------

def test_exit_to_unknown_room_raises(tmp_path, world_data):
    world_data["zones"]["village"]["rooms"]["square"]["exits"]["south"] = {"room": "tavrn"}
    with pytest.raises(ValueError, match="tavrn"):
        load_world(write_world(tmp_path, world_data))


def test_unknown_start_room_raises(tmp_path, world_data):
    world_data["world"]["start"]["room"] = "nowhere"
    with pytest.raises(ValueError, match="nowhere"):
        load_world(write_world(tmp_path, world_data))


def test_unknown_start_zone_raises(tmp_path, world_data):
    world_data["world"]["start"]["zone"] = "forest"
    with pytest.raises(ValueError, match="forest"):
        load_world(write_world(tmp_path, world_data))


def test_unknown_entry_room_raises(tmp_path, world_data):
    world_data["zones"]["cave"]["entry_room"] = "nowhere"
    with pytest.raises(ValueError, match="nowhere"):
        load_world(write_world(tmp_path, world_data))