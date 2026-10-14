from typing import Protocol

class HasHealth(Protocol):
    health: int
    
    @property
    def max_health(self) -> int:
        ...

EFFECTS = {}

def register_effect(name):
    def decorator(func):
        EFFECTS[name] = func
        return func
    return decorator

@register_effect("heal")
def heal(amount: int, target: HasHealth) -> None:
    if amount <= 0:
        raise ValueError("Invalid heal amount")
    
    target.health = min(target.max_health, target.health + amount)
