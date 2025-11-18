from typing import List

class World:
    def __init__(self):
        self.name = "Game World"
        self.starting_zone_id = ""
        self.zones = []
    
    def add_zone(self, zone: 'Zone'):
        self.zones.append(zone)
    
    def remove_zone(self, zone: 'Zone'):
        self.zones.remove(zone)
    
    def has_zone(self, zone_id: str) -> bool:
        return any(zone.id == zone_id for zone in self.zones)
    
    def get_zone(self, zone_id: str) -> 'Zone':
        for zone in self.zones:
            if zone.id == zone_id:
                return zone
        raise ValueError(f"Zone with id {zone_id} not found")
        
    
    def get_world_starting_zone(self) -> 'Zone':
        return self.get_zone(self.starting_zone_id)
    
    def get_world_starting_room(self) -> 'Room':
        starting_zone = self.get_zone(self.starting_zone_id)
        for room in starting_zone.rooms:
            if room.spawnpoint:
                return room
        raise ValueError("No spawnpoint room found in starting zone")
    
    def __str__(self):
        return f"World(name={self.name}, zones={len(self.zones)})"
    
    
    