from dataclasses import dataclass
from dataclasses import field
from character import Character

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
    instant_value: int = 0
    tick_value: int = 0
    duration: int
    remaining_duration: int = field(init=False)
    ignore_defense: bool = False
    flags: list = []

    def __post_init__(self):
        self.remaining_duration = self.duration

    def apply(self, target: Character):
        if "instant" in self.flags:
            match self.effect_type:
                case "damage":
                    damage = Damage(
                        amount=self.instant_value,
                        damage_type="physical",
                        source="Effect",
                        ignore_defense=self.ignore_defense
                    )
                    target.take_damage(damage)
                case "heal":
                    target.health += self.instant_value
                    target.health = min(target.max_health, target.health)
                case "buff_strength":
                    target.strength += self.instant_value

    def tick(self, target):
        if "over_time" in self.flags:
            match self.effect_type:
                case "damage":
                    damage = Damage(
                        amount=self.tick_value,
                        damage_type="physical",
                        source="Effect",
                        ignore_defense=self.ignore_defense,
                        is_dot=True
                    )
                    target.take_damage(damage)
                case "heal":
                    target.health += self.tick_value
                    target.health = min(target.max_health, target.health)
                case "buff_strength":
                    target.strength += self.tick_value
            self.remaining_duration -= 1

        
    def expire(self, target):
        if "buff_strength" in self.effect_type:
            target.strength -= (self.instant_value + self.tick_value * (self.duration - self.remaining_duration))

    def duration_tick(self):
        self.remaining_duration -= 1


@dataclass
class CastTime:
    name: str
    cast_time: int  
    effect: Effect
    block_action: bool = False
    def __str__(self):
        return f"Casting {self.name} for {self.cast_time} turns."
    