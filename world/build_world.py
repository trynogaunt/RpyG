from world.zone import Zone
from world.world import World
from world.room import Room, connect

def build_world():
    world = World()
    # Create Zones
    forest_zone = Zone("Enchanted Forest", "A mystical forest filled with magical creatures.")
    dungeon_zone = Zone("Dark Dungeon", "A gloomy dungeon crawling with monsters.")
    # Create Rooms for Forest Zone
    clearing = Room("Forest Clearing", "A sunny clearing surrounded by tall trees.")
    forest_zone.add_room(clearing)
    # Create Rooms for Dungeon Zone
    entrance = Room("Dungeon Entrance", "The dark entrance to the dungeon.")
    dungeon_zone.add_room(entrance)
    # Connect Rooms
    connect(clearing, entrance, "south", "north")
    # Add Zones to World
    world.add_zone(forest_zone)
    world.add_zone(dungeon_zone)
    return world