from dataclasses import dataclass
from dataclasses import field
from typing import Literal, Optional, TYPE_CHECKING

ActionType = Literal["attack", "defend", "inventory", "flee"]

if TYPE_CHECKING:
    from classes.character import Character
    from classes.Item import Item


@dataclass
class Damage:
    amount: int
    damage_type: str 
    source: str      
    ignore_defense: bool = False
    is_critical: bool = False
    is_dot: bool = False

    def __str__(self):
        crit_text = " (Critical Hit!)" if self.is_critical else ""
        return f"{self.source} deals {self.amount} {self.damage_type} damage{crit_text}."