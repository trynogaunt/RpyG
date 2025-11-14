from creation import create_hero


if __name__ == "__main__":
    hero = create_hero()
    print(f"Hero {hero.name} created with {hero.health} health and {hero.strength} strength.")
    print("Is the hero alive?", hero.is_alive())
    print("Hero's inventory items:", hero.inventory.list_items())
    print("Hero's equipped items:", hero.inventory.equipped_items)
    print("Hero's effects:", hero.effects)
    # Further game logic can be added here