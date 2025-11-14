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
    def __init__(self, name: str, description: str, damage: int, allowed_parts=None):
        super().__init__(name, description, allowed_parts)
        self.damage = damage
        self.type = "Weapon"

    def __str__(self):
        return f"{self.name}"

    def use(self, target, hero_strength=1):
        damage_taken = target.take_damage(self.damage * hero_strength)
        return f"{target.name} takes {damage_taken} damage from {self.name}!"

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