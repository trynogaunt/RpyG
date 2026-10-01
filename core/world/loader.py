import json
from pathlib import Path

from core.enums import Direction
from core.world.models import Room, RoomRef, World, Zone


def load_world(data_dir) -> World:
    data_dir = Path(data_dir)
    world_config = _read_json(data_dir / "world.json")

    raw_zones = {
        zone_id: _read_json(data_dir / "zones" / f"{zone_id}.json")
        for zone_id in world_config["zones"]
    }
    entries = load_entries(raw_zones)

    zones = {
        zone_id: load_zone(zone_data, entries)
        for zone_id, zone_data in raw_zones.items()
    }

    start = RoomRef(world_config["start"]["zone"], world_config["start"]["room"])
    world = World(start=start, zones=zones)
    validate_world(world)
    return world


def _read_json(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_entries(raw_zones: dict[str, dict]) -> dict[str, RoomRef]:
    return {
        zone_id: RoomRef(zone_id, zone_data["entry_room"])
        for zone_id, zone_data in raw_zones.items()
    }


def load_zone(zone_data: dict, entries: dict[str, RoomRef]) -> Zone:
    return Zone(
        id=zone_data["id"],
        name=zone_data["name"],
        description=zone_data["description"],
        entry_room=zone_data["entry_room"],
        rooms=load_rooms(zone_data, entries),
    )


def load_rooms(zone_data: dict, entries: dict[str, RoomRef]) -> dict[str, Room]:
    zone_id = zone_data["id"]
    rooms = {}
    for room_id, room_data in zone_data["rooms"].items():
        rooms[room_id] = Room(
            name=room_data["name"],
            description=room_data["description"],
            ref=RoomRef(zone_id, room_id),
            look_around=room_data.get("look_around", ""),
            exits=load_exits(room_data.get("exits", {}), zone_id, room_id, entries),
        )
    return rooms


def load_exits(raw_exits: dict, zone_id: str, room_id: str,
               entries: dict[str, RoomRef]) -> dict[Direction, RoomRef]:
    exits = {}
    for dir_str, target in raw_exits.items():
        where = f"sortie '{dir_str}' de {zone_id}/{room_id}"

        try:
            direction = Direction[dir_str.upper()]
        except KeyError:
            raise ValueError(f"Direction inconnue : {where}") from None

        target_zone = target.get("zone", zone_id)
        if target_zone not in entries:
            raise ValueError(f"Zone inconnue '{target_zone}' : {where}")

        if "room" in target:
            exits[direction] = RoomRef(target_zone, target["room"])
        else:
            exits[direction] = entries[target_zone]
    return exits

def validate_world(world: World) -> None:

    try:
        world.get_room(world.start)
    except ValueError as e:
        raise ValueError(f"Départ invalide : {e}") from None

    for zone in world.zones.values():
        try:
            world.get_room(RoomRef(zone.id, zone.entry_room))
        except ValueError as e:
            raise ValueError(f"Entrée de la zone '{zone.id}' invalide : {e}") from None

        for room_id, room in zone.rooms.items():
            for direction, target in room.exits.items():
                try:
                    world.get_room(target)
                except ValueError as e:
                    raise ValueError(
                        f"Sortie {direction.name} de {zone.id}/{room_id} invalide : {e}"
                    ) from None