from dataclasses import dataclass
from dataclasses import field
from typing import Literal, Optional, TYPE_CHECKING

ActionType = Literal["attack", "defend", "inventory", "flee"]

if TYPE_CHECKING:
    from classes.character import Character
    from classes.Item import Item


@dataclass
class Effect:
    name: str
    duration: int
    effect_type: Literal["damage", "heal", "buff_strength"]
    instant_value: int = 0
    tick_value: int = 0
    remaining_duration: int = field(init=False)
    ignore_defense: bool = False
    flags: list[str] = field(default_factory=list)
    total_applied: int = 0

    def __post_init__(self):
        self.remaining_duration = self.duration

    def apply(self, target: "Character"):
        if "instant" in self.flags:
            self._apply_effect_value(target, self.instant_value)

    def tick(self, target):
        if "over_time" in self.flags and not self.is_expired():
            self._apply_effect_value(target, self.tick_value)
            self.duration_tick()

    def _apply_effect_value(self, target: "Character", value: int):
        match self.effect_type:
            case "damage":
                damage = Damage(
                    amount=value,
                    damage_type="physical",
                    source=self.name,
                    ignore_defense=self.ignore_defense,
                    is_dot="over_time" in self.flags
                )
                target.take_damage(damage)
            case "heal":
                target.health += value
                target.health = min(target.max_health, target.health)
            case "buff_strength":
                target.strength += value
                self.total_applied += value
            
    def expire(self, target: "Character"):
        if "buff_strength" == self.effect_type:
            # Revert the strength buff when the effect expires, instant value if exists + total amount from ticks and duration
            target.strength -= self.total_applied
            
    def duration_tick(self):
        self.remaining_duration -= 1

    def is_expired(self):
        return self.remaining_duration <= 0
