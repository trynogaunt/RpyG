from classes.damages import Damage

class Item:
    def __init__(self, name, description="", allowed_parts=None):
        self.name = name
        self.description = description
        self.type = "Generic"
        self.allowed_parts = allowed_parts if allowed_parts else []

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
        super().__init__(name, description, allowed_parts)
        self.damage = damage
        self.damage_type = damage_type
        self.type = "Weapon"
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
        super().__init__(name, description, allowed_parts)
        self.type = "Armor"
        self.defense = defense
        self.part = part  # e.g., head, torso, legs, feet

    def use(self, target):
        target.health += self.defense
        return f"{target.name} gains {self.defense} health from {self.name}!"

class Consumable(Item):
    def __init__(self, name, description, value, effect):
        super().__init__(name, description, value)
        self.type = "Consumable"
        self.effect = effect  # e.g., healing amount

    def use(self, target):
        target.health += self.effect
        return f"{target.name} heals {self.effect} health from {self.name}!"