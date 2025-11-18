from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Room:
    id : str
    name : str
    description : str
    exits : Dict[str, 'Room'] = field(default_factory=dict)
    enemies : List[str] = field(default_factory=list)
    items : List[str] = field(default_factory=list)
    npc : List[str] = field(default_factory=list)
    spawnpoint : bool = False