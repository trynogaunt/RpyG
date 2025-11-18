from world.build_world import *
from enum import Enum, auto
from world.world import World

def test_build_zone():
    zone = load_zone_from_file("world/zones/entry_village.json")
    assert zone.name == "Entry Village"
    assert len(zone.rooms) == 4 
    room_names = [room.name for room in zone.rooms]
    assert "Village Square" in room_names
    return zone

def test_build_multiple_zones():
    zones = list(load_zones("world/zones"))
    assert len(zones) >= 2  
    zone_names = [zone.name for zone in zones]
    assert "Entry Village" in zone_names
    assert "Flooded Cave" in zone_names
    return zones

def test_build_world():
    world = load_world("world/zones")
    assert isinstance(world, World)
    assert len(world.zones) >= 2  
    zone_ids = [zone.id for zone in world.zones]
    assert "entry_village" in zone_ids
    assert "flooded_cave" in zone_ids
    world_starting_room = world.get_world_starting_room()
    assert world_starting_room.name == "Village Square"
    assert world_starting_room.spawnpoint is True
    assert len(world.zones[0].rooms) == 4
    return world

if __name__ == "__main__":
    print(test_build_world())