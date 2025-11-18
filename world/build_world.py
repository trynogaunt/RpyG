from world.zone import Zone
from world.world import WorldMap, WorldZone
from world.room import Room
import json
import os
from typing import List

def build_world():
    pass
def load_world_from_file(file_path: str) -> WorldMap:
    # Placeholder for loading world from a file
    pass

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