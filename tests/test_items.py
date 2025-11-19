def test_items():
    from models.item import Item, Consumable, Weapon, Armor
    sword = Weapon(name="Sword", description="A sharp blade.", damage=10, damage_type="physical")
    assert sword.name == "Sword"
    assert sword.damage == 10
    assert sword.make_damage(user=type('User', (object,), {'name': 'Hero'})(), target=None).amount == 10
    armor = Armor(name="Shield", description="Protects you.", defense=5, part="torso")
    assert armor.defense == 5
    potion = Consumable(name="Health Potion", description="Restores health.", effect_type="heal", value=20)
    assert potion.effect_type == "heal"
    assert potion.value == 20
    class Dummy:
        def __init__(self, name):
            self.name = name
            self.health = 50
            self.max_health = 100
            self.strength = 10
    user = Dummy(name="Hero")
    target = Dummy(name="Ally")
    heal_msg = potion.use(user, target)
    assert target.health == 70
    assert heal_msg == "Ally heals 20 health from Health Potion!"
    buff_potion = Consumable(name="Strength Potion", description="Increases strength.", effect_type="buff_strength", value=5)
    buff_msg = buff_potion.use(user, target)
    assert target.strength == 15
    assert buff_msg == "Ally gains 5 strength from Strength Potion!"
    damage_potion = Consumable(name="Damage Potion", description="Deals damage.", effect_type="damage", value=15)
    damage = damage_potion.make_damage(user, target)
    assert damage.amount == 15
    assert damage.damage_type == "physical"
    assert damage.source == "Hero"
    print("All item tests passed!")
    
if __name__ == "__main__":
    test_items()
    