from dataclasses import dataclass

@dataclass
class Damage:
    amount: int
    damage_type: str 
    source: str      
    ignore_defense: bool = False
    is_critical: bool = False

    def __str__(self):
        crit_text = " (Critical Hit!)" if self.is_critical else ""
        return f"{self.source} deals {self.amount} {self.damage_type} damage{crit_text}."

@dataclass
class Effect:
    def __init__(self, name: str, effect_type: str, value: int, duration: int, damage_type: Damage = None):
        self.name = name
        self.effect_type = effect_type  
        self.value = value              
        self.duration = duration        
        self.remaining_duration = duration
        

    def apply(self, target):
        match self.effect_type:
            case "heal":
                target.health += self.value
                target.health = min(target.max_health, target.health)
                return f"{target.name} heals {self.value} health from {self.name}!"
            case "buff_strength":
                target.strength += self.value
                return f"{target.name} gains {self.value} strength from {self.name}!"
            case "debuff_strength":
                target.strength -= self.value
                return f"{target.name} loses {self.value} strength from {self.name}!"
            case da

    def tick(self, target):
        pass
        
    def expire(self, target):
        pass

    def duration_tick(self):
        if self.remaining_duration > 0:
            self.remaining_duration -= 1

@dataclass
class CastTime:
    name: str
    cast_time: int  
    effect: Effect
    block_action: bool = False
    def __str__(self):
        return f"Casting {self.name} for {self.cast_time} turns."
    