from classes.interface_class import CastTime
from models.damage import Damage
from models.effect import Effect

class Item:
    def __init__(self, name, description="", item_type="Generic"):
        self.description = description
        self.type = item_type
        self.name = name
    def use(self, target):
        raise NotImplementedError("This method should be overridden by subclasses.")

class Weapon(Item):
    """Weapon item that can be used to attack targets.
    Attributes:
        name (str): The name of the weapon. (herited from Item)
        description (str): A brief description of the weapon. (herited from Item)
        damage (int): The damage this weapon can inflict.
        type (str): The type of the item, set to "Weapon".
    """
    def __init__(self, name: str, description: str, damage: int, damage_type: str, ignore_defense=False, allowed_parts=None, two_handed=False):
        super().__init__(name, description, "Weapon")
        self.damage = damage
        self.damage_type = damage_type
        self.ignore_defense = ignore_defense
        self.two_handed = two_handed

    def __str__(self):
        return f"{self.name}"

    def make_damage(self, user, target) -> Damage:
        return Damage(
            amount=self.damage,
            damage_type=self.damage_type,
            source=user.name,
            ignore_defense=self.ignore_defense
        )

class Armor(Item):
    def __init__(self, name, description, defense, part=None, allowed_parts=None):
        super().__init__(name, description, "Armor")
        self.defense = defense
        self.part = part  # e.g., head, torso, legs, feet
        self.allowed_parts = allowed_parts if allowed_parts else [part]
    def use(self, target):
        target.health += self.defense
        return f"{target.name} gains {self.defense} health from {self.name}!"

class Consumable(Item):
    def __init__(self, name, description, effect_type ,value, duration=0, cast_time=0, block_action=False):
        super().__init__(name, description, "Consumable")
        self.value = value
        self.effect_type = effect_type 
        self.effect_value = value
        self.duration = duration
        self.cast_time = cast_time  
        self.block_action = block_action  

    def use(self, user, target):
        match self.effect_type:
            case "heal":
                target.health += self.effect_value
                target.health = min(target.max_health, target.health)
                return f"{target.name} heals {self.effect_value} health from {self.name}!"
            case "buff_strength":
                target.strength += self.effect_value
                return f"{target.name} gains {self.effect_value} strength from {self.name}!"
            case "damage":
                damage = self.make_damage(user=user, target=target)
                
    def make_damage(self, user, target) -> Damage:
                return Damage(
                    amount=self.effect_value,
                    damage_type="physical",
                    source=user.name
                )