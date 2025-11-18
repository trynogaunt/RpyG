from world.zone import Zone
from world.world import World
from world.room import Room
import json
import os
from typing import List

def load_world(directory_path: str) -> World:
    world = World()
    zones = list(load_zones(directory_path))
    for zone in zones:
        world.add_zone(zone)
    if zones:
        world.starting_zone_id = zones[0].id
    return world

def load_zones(directory_path: str) -> List[Zone]:
    for filename in os.listdir(directory_path):
        if filename.endswith('.json') and not filename.startswith('.'):
            zone = load_zone_from_file(os.path.join(directory_path, filename))
            yield zone

def load_zone_from_file(file_path: str) -> Zone:
    if file_path.endswith('.json'):
        with open(file_path, 'r') as f:
            data = json.load(f)
            rooms = []
            for each_room in data.get("rooms", []):
                room = Room(
                    id=each_room["id"],
                    name=each_room["name"],
                    description=each_room["description"],
                    exits= each_room["exits"],
                    enemies= each_room.get("enemies", []),
                    items= each_room.get("items", []),
                    npc= each_room.get("npc", []),
                    spawnpoint= each_room.get("spawnpoint", False),
                    look_around_text= each_room.get("look_around_text", None),
                )
                rooms.append(room)

            zone = Zone(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                entry_room_id=data.get("entry_room_id"),
                rooms=rooms,
            )
            return zone
    else:
        raise ValueError("Unsupported file format")