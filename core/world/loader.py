import json
import os
from pathlib import Path

from core.world.models import World, Zone, Room, RoomRef

def load_world(data_dir):
    world_path = Path(data_dir) / 'world.json'
    with open(world_path, 'r') as f:
        return json.load(f)

def load_zone(data_dir, zone_id):
    zone_path = Path(data_dir) / f'{zone_id}.json'
    with open(zone_path, 'r', encoding='utf-8') as f:
        zone_data = json.load(f)
        zone_id = zone_data["id"]
        zone_name = zone_data["name"]
        zone_description = zone_data["description"]
        zone_entry_room = zone_data["entry_room"]
        rooms = load_zone_rooms(zone_data)
        return Zone(id=zone_id, 
            rooms=rooms, 
            name=zone_name, 
            description=zone_description,
            entry_room=zone_entry_room)

def load_zone_rooms(zone_data):
    zone_id = zone_data["id"]
    rooms = {}

    for room_id, room_data in zone_data["rooms"].items():
        room_name = room_data["name"]
        room_description = room_data["description"]
        room_look_around = room_data.get("look_around", "")
        room_exits = room_data.get("exits", {})
        room_ref = RoomRef(zone_id=zone_id, room_id=room_id)
        room = Room(
            name=room_name,
            description=room_description,
            ref=room_ref,
            look_around=room_look_around,
            exits=room_exits
        )
        rooms[room_id] = room
    return rooms
