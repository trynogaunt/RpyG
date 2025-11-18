from dataclasses import dataclass, field
from typing import List

@dataclass
class WorldMap:
    zones: List['Zone'] = field(default_factory=list)
        
    def add_zone(self, zone : 'Zone'):
        self.zones.append(zone)
    
    def remove_zone(self, zone : 'Zone'):
        self.zones.remove(zone)

@dataclass
class WorldZone:
    id: str
    name: str
    description: str
    difficulty_level: int
    neighbors: List['WorldZone'] = field(default_factory=list)