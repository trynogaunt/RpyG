import dataclasses

@dataclasses.dataclass
class Damage:
    amount: int
    damage_type: str 
    source: str      
    ignore_defense: bool = False
    is_critical: bool = False