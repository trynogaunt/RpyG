from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Zone:    
    id : str
    name: str
    rooms: List['Room'] = field(default_factory=list)
    entry_room_id: Optional[str] = None
    
    description: str = ""
    
    def add_room(self, room : 'Room'):
        self.rooms.append(room)
        
    def remove_room(self, room : 'Room'):
        self.rooms.remove(room)