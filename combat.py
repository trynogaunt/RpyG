from ui_console import show_combat_ui, log_attack, show_victory, show_defeat

def run_combat(player, enemy):
    log_lines = []
    while player.health > 0 and enemy.health > 0:
        actions = ["Attack", "Use Item", "Flee"]
        choice = show_combat_ui(player, enemy, log_lines, actions)

        if choice == "Attack":
            damage_dealt = player.attack(enemy)
            log_lines.append(log_attack(player, enemy, damage_dealt))
            if enemy.health <= 0:
                show_combat_ui(player, enemy, log_lines, actions)
                loot = enemy.inventory.items
                show_victory(player, enemy, loot)
                for item in loot:
                    player.inventory.add_item(item)
                return True
            else:
                damage_dealt = enemy.attack(player)
                log_lines.append(log_attack(enemy, player, damage_dealt))
                if player.health <= 0:
                    show_combat_ui(player, enemy, log_lines, actions)
                    show_defeat()
                    return False
        elif choice == "Use Item":
            pass  
        elif choice == "Flee":
            print(f"{player.name} fled from combat!")
            return False