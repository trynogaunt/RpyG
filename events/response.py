from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from enum import Enum, auto
from typing import Literal, List, Optional, Dict, Any
from models.damage import Damage

@dataclass
class DamageResult:
    attacker_id: str        
    target_id: str
    damage: Damage         
    final_amount: int       
    target_was_alive: bool
    target_is_dead: bool
    
    

class ResponseType(Enum):
    DAMAGE = auto()
    EFFECT = auto()
    BATTLE_END = auto()
    SYSTEM = auto()
    DIALOGUE = auto()
    STATE_CHANGE = auto()
    ROOM_ENTERED = auto()
    MOVE_BLOCKED = auto()
    MAIN_MENU = auto()
    CHARACTER_CREATION = auto()
   
   
@dataclass
class MoveResult:
    moved: bool
    from_room: Any
    to_room: Any
    used_exit: str
    enemies: List[Any]
    exits: Dict[str, Any] 

@dataclass
class GameResponse:
    type: ResponseType
    message: str
    tags: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    
    