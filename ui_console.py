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

def show_combat(hero, enemy):
    print(f"{hero.name} - Health: {hero.health}, Strength: {hero.strength}")
    print(f"{enemy.name} - Health: {enemy.health}, Strength: {enemy.strength}")

def show_inventory(hero):
    pass # To be implemented

def show_victory(hero, enemy, loot: list):
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
    lines = [
        "Defeat!",
        "You have been defeated. Better luck next time!",    
    ]
    max_line_length = max(len(line) for line in lines)

    for line in lines:
        print(line.ljust(max_line_length))


def show_combat_ui(hero, enemy, log_lines, actions):
    header = f"=========== Combat: {hero.name} vs {enemy.name} ==========="
    stats_view = (
        f"{hero.name} - Health: {hero.health}, Strength: {hero.strength}\n"
        f"{enemy.name} - Health: {enemy.health}, Strength: {enemy.strength}\n"
    )
    last_logs = log_lines[-5:]  # Show last 5 log lines

    print(header)
    

