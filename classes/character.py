from classes import inventory
class Character:
    def __init__(self, name, health=10, strength=1, luck=0):
        self.name = name
        self.health = health
        self.strength = strength
        self.effects = []
        self.luck = luck
        self.inventory = inventory.Inventory()  # To be assigned an Inventory instance
    
    def attack(self, target):
        for item in self.inventory.equipped_items.values():
            if item and item.type == "Weapon":
                item.use(target)
                return f"{self.name} attacks {target.name} with {item.name} for {damage} damage!"
        target.health -= self.strength
        return f"{self.name} attacks {target.name} for {self.strength} damage!"

    def apply_effect(self, effect):
        self.effects.append(effect)
    
    def retire_effect(self, effect):
        if effect in self.effects:
            self.effects.remove(effect)
    
    def use_effects(self):
        for effect in self.effects:
            effect.apply(self)

    def take_damage(self, damage):
        total_defense = 0
        for item in self.inventory.equipped_items.values():
            if item and item.type == "Armor":
                total_defense += item.defense
        damage -= total_defense
        self.health -= damage
        return damage