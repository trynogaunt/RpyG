def test_items():
    from models.item import Item, Consumable, Weapon, Armor
    sword = Weapon(name="Sword", description="A sharp blade.", damage=10, damage_type="physical", allowed_slots=["right_hand", "left_hand"], two_handed=False)
    assert sword.name == "Sword"
    assert sword.damage == 10
    assert sword.make_damage(user=type('User', (object,), {'name': 'Hero'})(), target=None).amount == 10
    armor = Armor(name="Shield", description="Protects you.", defense=5, allowed_slots=["torso"])
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

def test_add_in_inventory():
    from models.item import Item
    from models.hero import Hero
    from models.enemy import Enemy
    char = Hero(name="TestHero", health=100, strength=10, luck=5, speed=7, gold=50)
    enemy = Enemy(name="TestEnemy", health=80, strength=8, speed=6, luck=3)
    item1 = Item(name="Ring", description="A golden ring.")
    item2 = Item(name="Amulet", description="A magical amulet.")
    char.add_to_inventory(item1)
    enemy.add_to_inventory(item2)
    assert len(char.inventory.items) == 1
    assert char.inventory.items[0].name == "Ring"
    assert len(enemy.inventory.items) == 1
    assert enemy.inventory.items[0].name == "Amulet"

def test_equip_item():
    from models.item import Weapon, Armor
    from models.hero import Hero
    char = Hero(name="EquipHero", health=100, strength=10, luck=5, speed=7, gold=50)
    sword = Weapon(name="Sword", description="A sharp blade.", damage=10, damage_type="physical", allowed_slots=["right_hand", "left_hand"], two_handed=False)
    shield = Armor(name="Shield", description="Protects you.", defense=5, allowed_slots=["left_hand", "right_hand"])
    dagger = Weapon(name="Dagger", description="A small blade.", damage=5, damage_type="physical", allowed_slots=["left_hand", "right_hand"], two_handed=False, ignore_defense=True)
    heavy_sword = Weapon(name="Heavy Sword", description="A two-handed heavy blade.", damage=20, damage_type="physical", allowed_slots=["left_hand", "right_hand"], two_handed=True)
    char.add_to_inventory(sword)
    char.add_to_inventory(shield)
    char.add_to_inventory(dagger)
    char.add_to_inventory(heavy_sword)
    char.equip_item(sword, "right_hand")
    char.equip_item(shield, "left_hand")
    equipped_items = char.inventory.list_equipped_items()
    assert len(equipped_items) == 2
    assert any(item.name == "Sword" for slot, item in equipped_items)
    assert any(item.name == "Shield" for slot, item in equipped_items)
    char.unequip_item("right_hand")
    equipped_items = char.inventory.list_equipped_items()
    assert len(equipped_items) == 1
    char.equip_item(sword, "left_hand")
    equipped_items = char.inventory.list_equipped_items()
    assert len(equipped_items) == 1
    assert equipped_items[0][1].name == "Sword"
    char.equip_item(dagger, "right_hand")
    equipped_items = char.inventory.list_equipped_items()
    assert len(equipped_items) == 2
    assert any(item.name == "Dagger" for slot, item in equipped_items)
    assert any(item.name == "Sword" for slot, item in equipped_items)
    char.equip_item(heavy_sword, "left_hand")
    equipped_items = char.inventory.list_equipped_items()
    assert len(equipped_items) == 2
    assert all(item.name == "Heavy Sword" for slot, item in equipped_items)
    assert any(item.name == "Sword" for item in char.inventory.list_items())
    assert any(item.name == "Dagger" for item in char.inventory.list_items())
    assert any(item.name == "Shield" for item in char.inventory.list_items())
    print(f"Equipped items after tests: {[str(item) for slot, item in char.inventory.list_equipped_items()]}")
    print(f"Inventory items after tests: {[str(item) for item in char.inventory.list_items()]}")
if __name__ == "__main__":
    test_items()
    test_add_in_inventory()
    test_equip_item()
    print("All tests passed.")
    