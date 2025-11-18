from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Room:
    id : str
    name : str
    description : str
    exits : Dict[str, 'Room'] = field(default_factory=dict)