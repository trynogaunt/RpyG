from dataclasses import dataclass
from dataclasses import field
from typing import Literal, Optional, TYPE_CHECKING

ActionType = Literal["attack", "defend", "inventory", "flee"]

if TYPE_CHECKING:
    from classes.character import Character
    from classes.Item import Item
    from models.effect import Effect

@dataclass
class CastTime:
    name: str
    cast_time: int  
    effect: "Effect"
    block_action: bool = False
    def __str__(self):
        return f"Casting {self.name} for {self.cast_time} turns."


@dataclass
class ActionCombatChoice:
    actor: "Character"
    action: ActionType
    target: Optional["Character"] = None
    item: Optional["Item"] = None
    
@dataclass
class CharacterCreationState:
    name: str = ""
    health: int = 10
    strength: int = 1
    luck: int = 0
    speed: int = 1
    points_to_spend: int = 5
    step: int = 1  
    error : str = ""

