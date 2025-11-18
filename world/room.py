from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Room:
    id : str
    name : str
    description : str
    exits : Dict[str, 'Room'] = field(default_factory=dict)
    exit_to_zone : Optional[str] = None
    exit_to_zone_entry : Optional[str] = None