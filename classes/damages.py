import dataclasses

@dataclasses.dataclass
class Damage:
    amount: int
    damage_type: str  # e.g., "physical", "magical", etc.
    source: str       # e.g., "sword", "fireball", etc.
    ignore_defense: bool = False
    is_critical: bool = False