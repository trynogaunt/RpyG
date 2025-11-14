import questionary
import os
import time


def main_menu():
    menu_items = [
        "Start New Game",
        "Exit"
    ]

    lines = [
        "RPyG Engine Demo",
        "Prototype build 0.1.0 – Single fight demo",    
    ]

    max_line_length = max(len(line) for line in lines)
    border = "=" * (max_line_length + 4)

    print(border)
    for line in lines:
        print(f"| {line.ljust(max_line_length)} |")
    print(border)

    choice = questionary.select(
        "Main Menu - Choose an option:",
        choices=menu_items,
    ).ask()
    if choice == "Start New Game":
        return "new_game"
    elif choice == "Exit":
        return "exit"


def splash():
    STONE = "\033[37m"
    GOLD = "\033[33m"
    RESET = "\033[0m"

    R = [
        "██████╗",
        "██╔══██╗",
        "██║  ██║",
        "██████╔╝",
        "██╔══██╗",
        "██║  ██║",
        "╚═╝  ╚═╝",
    ]

    P = [
        "██████╗",
        "██╔══██╗",
        "██████╔╝",
        "██╔═══╝ ",
        "██║     ",
        "██║     ",
        "╚═╝     ",
    ]

    Y = [
        "██╗   ██╗",
        "╚██╗ ██╔╝",
        " ╚████╔╝ ",
        "  ╚██╔╝  ",
        "   ██║   ",
        "   ██║   ",
        "   ╚═╝   ",
    ]

    G = [
        " ██████╗",
        "██╔════╝",
        "██║  ███╗",
        "██║   ██║",
        "██║   ██║",
        "╚██████╔╝",
        " ╚═════╝ ",
    ]

    slogan = f"{STONE}Your CPU will handle all the dragons.{RESET}"



    os.system("cls" if os.name == "nt" else "clear")

    # largeurs fixes par lettre
    wR = max(len(line) for line in R)
    wP = max(len(line) for line in P)
    wY = max(len(line) for line in Y)
    wG = max(len(line) for line in G)

    for i in range(len(R)):
        line = (
            f"{STONE}{R[i].ljust(wR)}{RESET}   "
            f"{STONE}{P[i].ljust(wP)}{RESET}   "
            f"{STONE}{Y[i].ljust(wY)}{RESET}   "
            f"{GOLD}{G[i].ljust(wG)}{RESET}"
        )
        print(line)
        time.sleep(0.08)

    print()
    time.sleep(0.3)
    print(slogan)
    time.sleep(1.0)


def log_attack(attacker, target, damage_dealt):
    print(f"{attacker.name} dealt {damage_dealt} damage to {target.name}!")
    return f"{attacker.name} dealt {damage_dealt} damage to {target.name}!"

def show_combat(hero, enemy):
    print(f"{hero.name} - Health: {hero.health}, Strength: {hero.strength}")
    print(f"{enemy.name} - Health: {enemy.health}, Strength: {enemy.strength}")


def show_inventory(hero):
    pass # To be implemented

def show_room(player, msg = None):
    room = player.current_room
    os.system("cls" if os.name == "nt" else "clear")
    lines = [
        f"{room.name}",
        room.description,
    ]
    max_line_length = max(len(line) for line in lines)

    print("=" * (max_line_length + 4))
    for line in lines:
        print(f"| {line.ljust(max_line_length)} |")
    print("=" * (max_line_length + 4))
    if msg:
        print(msg)
    
    time.sleep(2)

def on_enter_room(player):
    room = player.current_room
    os.system("cls" if os.name == "nt" else "clear")
    lines = [
        f"You have entered: {room.name}",
        room.description,
    ]
    max_line_length = max(len(line) for line in lines)

    print("=" * (max_line_length + 4))
    for line in lines:
        print(f"| {line.ljust(max_line_length)} |")
    print("=" * (max_line_length + 4))

    time.sleep(2)

def no_changed_room(player):
    on_enter_room(player)
    print("No exist exit in that direction.")
    time.sleep(2)

def show_room_ennemies(room):
    if room.enemies:
        print("Enemies present in the room:")
        for enemy in room.enemies:
            print(f"- {enemy.name} (Health: {enemy.health}, Strength: {enemy.strength})")
    else:
        print("No enemies in this room.")
    time.sleep(2)

def ask_player_action(player, actions):
    choice = questionary.select(
        "Choose your action:",
        choices=actions
    ).ask()
    return choice

def ask_direction(room) -> str:
    directions = list(room.exits.keys())
    choice = questionary.select(
        "Choose a direction to move:",
        choices=directions
    ).ask()
    return choice

def show_victory(hero, enemy, loot: list):
    os.system("cls" if os.name == "nt" else "clear")
    lines = [
        "Victory!",
        f"You have defeated {enemy.name} and earned the following loot:",    
    ]
    for item in loot:
        lines.append(f"- {item.name}")
    max_line_length = max(len(line) for line in lines)

    for line in lines:
        print(line.ljust(max_line_length))

def show_defeat():
    os.system("cls" if os.name == "nt" else "clear")
    lines = [
        "Defeat!",
        "You have been defeated. Better luck next time!",    
    ]
    max_line_length = max(len(line) for line in lines)

    for line in lines:
        print(line.ljust(max_line_length))


def show_combat_ui(hero, enemy, log_lines, actions):
    os.system("cls" if os.name == "nt" else "clear")
    header = f"=========== Combat: {hero.name} vs {enemy.name} ==========="
    stats_hero = {
        "Name": f"{hero.name}", "HP": f"{hero.health}/{hero.max_health}", "STR": f"{hero.strength}", "DEF" : f"{hero.defense}", "LCK": f"{hero.luck}"
    }
    stats_enemy = {
        "Name": f"{enemy.name}", "HP": f"{enemy.health}/{enemy.max_health}", "STR": f"{enemy.strength}", "DEF" : f"{enemy.defense}", "LCK": f"{enemy.luck}"
    }

    hero_filled_length = int(20 * hero.hp_ratio)
    enemy_filled_length = int(20 * enemy.hp_ratio)

    filled_bar_hero = "█" * hero_filled_length + "░" * (20 - hero_filled_length)
    filled_bar_enemy = "█" * enemy_filled_length + "░" * (20 - enemy_filled_length)

    space_between_cols = 5

    left_col = [stats_hero["Name"], f"HP: {filled_bar_hero} {stats_hero['HP']}", f"STR: {stats_hero['STR']}", f"DEF: {stats_hero['DEF']}", f"LCK: {stats_hero['LCK']}"]
    right_col = [stats_enemy["Name"], f"HP: {filled_bar_enemy} {stats_enemy['HP']}", f"STR: {stats_enemy['STR']}", f"DEF: {stats_enemy['DEF']}", f"LCK: {stats_enemy['LCK']}"]

    left_col_max_width = max(len(line) for line in left_col)
    print(header)
    for i in range(len(left_col)):
        line = left_col[i].ljust(left_col_max_width) + " " * space_between_cols + right_col[i]
        print(line)
    
    if len(log_lines) == 0:
        last_logs = ["Combat just started."]
    else:
        last_logs = log_lines[-5:]

    print("\n--- Combat Log ---")
    for log in last_logs:
        print(log)
    print("\n--- Actions ---")
    next_action = questionary.select(
        "Choose your action:",
        choices=actions
    ).ask()        

    return next_action

if __name__ == "__main__":
    hero = type("Hero", (), {"name": "Hero", "health": 15, "max_health": 20, "strength": 5, "defense": 2, "luck": 1, "hp_ratio": 0.75})()
    enemy = type("Enemy", (), {"name": "Goblin", "health": 8, "max_health": 15, "strength": 3, "defense": 1, "luck": 0, "hp_ratio": 0.53})()
    show_combat_ui(hero, enemy, ["Hero attacks Goblin for 3 damage!", "Goblin attacks Hero for 2 damage!"], ["Attack", "Use Item", "Flee"])

    
    

