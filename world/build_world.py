from world.zone import Zone
from world.world import World
from world.room import Room
import json
import os
from typing import List

def load_world(directory_path: str) -> World:
    world = World()
    zones = list(load_zones(directory_path))
    return World(zones)
    

def load_zones(directory_path: str) -> List[Zone]:
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
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