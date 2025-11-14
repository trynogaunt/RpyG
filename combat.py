def start_combat(player, enemy):
    print(f"A wild {enemy.name} appears!")
    while player.health > 0 and enemy.health > 0:
        action = questionary.select(
            "Choose your action:",
            choices=["Attack", "Use Item", "Flee"]
        ).ask()

        if action == "Attack":
            damage_dealt = player.attack(enemy)
            print(f"You dealt {damage_dealt} damage to {enemy.name}!")
        elif action == "Use Item":
            print("Item usage not implemented yet.")
        elif action == "Flee":
            print("You fled the combat!")
            return

        if enemy.health > 0:
            damage_received = enemy.attack(player)
            print(f"{enemy.name} dealt {damage_received} damage to you!")

    if player.health <= 0:
        print("You have been defeated!")
    else:
        print(f"You defeated {enemy.name}!")