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

def load_zone(file_path: str) -> Zone:
    with open(file_path, 'r') as file:
        zone_data = json.load(file)

    zone = Zone(
        id=zone_data['id'],
        name=zone_data['name'],
        description=zone_data['description']
    )

    for room_data in zone_data['rooms']:
        room = load_room
        zone.add_room(room)

    return zone
def load_room(file_path: str) -> Room:
    with open(file_path, 'r') as file:
        room_data = json.load(file)

    room = Room(
        id=room_data['id'],
        name=room_data['name'],
        description=room_data['description'],
        exits=room_data.get('exits', {}),
        enemies=room_data.get('enemies', []),
        items=room_data.get('items', []),
        npc=room_data.get('npc', []),
        spawnpoint=room_data.get('spawnpoint', False)
    )

    return room

def load_npc(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        npc_data = json.load(file)
    return npc_data