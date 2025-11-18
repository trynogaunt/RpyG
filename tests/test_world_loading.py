from world.build_world import *
from enum import Enum, auto
from world.world import WorldMap, WorldZone

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

if __name__ == "__main__":
    print(test_build_multiple_zones())