from dataclasses import dataclass

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

@dataclass
class Effect:
    name: str
    effect_type: str
    value: int
    duration: int
    remaining_duration: int = field(init=False)
    instant_damage: Damage = None
    tick_damage: Damage = None
    tick_heal: int = None
    flags: list = []

    def __post_init__(self):
        self.remaining_duration = self.duration
    def apply(self, target):
        if "instant" in flags:
            match self.effect_type:
                case "damage":
                    target.health -= self.damage_type.amount
                case "heal":
                    target.health += self.tick_heal.amount

    def tick(self, target):
        

        
    def expire(self, target):
        pass

    def duration_tick(self):
        pass


@dataclass
class CastTime:
    name: str
    cast_time: int  
    effect: Effect
    block_action: bool = False
    def __str__(self):
        return f"Casting {self.name} for {self.cast_time} turns."
    