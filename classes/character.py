from classes import inventory
from classes.damages import Damage
class Character:
    def __init__(self, name, health=10, strength=1, luck=0):
        self.name = name
        self.health = health
        self.max_health = health
        self.strength = strength
        self.effects = []
        self.luck = luck
        self.inventory = inventory.Inventory() 
    
    def attack(self, target):
        weapons = self.inventory.get_equipped_weapons()
        for weapon in weapons:
            damage = weapon.make_damage(self, target)
            actual_damage = target.take_damage(damage)
            return actual_damage


    def apply_effect(self, effect):
        self.effects.append(effect)
    
    def retire_effect(self, effect):
        if effect in self.effects:
            self.effects.remove(effect)
    
    def use_effects(self):
        for effect in self.effects:
            effect.apply(self)

    def take_damage(self, damage: Damage):
        amount = damage.amount
        if not damage.ignore_defense:
            defense = [item.defense for item in self.inventory.equipped_items.values() if item and item.type == "Armor"]
            amount -= sum(defense)
            amount = max(amount, 0) 
        else:
            amount = max(amount, 0)
        self.health -= amount
        self.health = max(self.health, 0) 
        return amount
    
    @property
    def defense(self):
        total_defense = sum(
            item.defense for item in self.inventory.equipped_items.values()
            if item and item.type == "Armor"
        )
        return total_defense
    
    @property
    def hp_ratio(self):
        return max(0, min(1, self.health / self.max_health)) if self.max_health > 0 else 0
