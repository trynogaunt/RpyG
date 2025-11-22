from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Zone:    
    id : str
    name: str
    rooms: List[str] = field(default_factory=list)
    entry_room_id: Optional[str] = None
    
    description: str = ""
    
    def add_room(self, room : 'Room'):
        self.rooms.append(room)
        
    def remove_room(self, room : 'Room'):
        self.rooms.remove(room)
        
    def get_room_by_id(self, room_id: str) -> 'Room':
        for room in self.rooms:
            if room.id == room_id:
                return room
        raise ValueError(f"Room with id {room_id} not found in zone {self.id}")