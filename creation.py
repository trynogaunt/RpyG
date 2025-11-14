from classes import hero
from items import COMMON_WEAPON as weapons
import questionary

POINTS_TO_DISTRIBUTE = 10

def create_hero():

    lines = [
        "Hero Creation",
        "Distribute your stat points and choose a starting weapon.",    
    ]

    max_line_length = max(len(line) for line in lines)
    border = "=" * (max_line_length + 4)
    print(border)
    for line in lines:
        print(f"| {line.ljust(max_line_length)} |")
    print(border)
    print("")

    name = questionary.text("Enter your hero's name:").ask()
    if name.strip().lower() == "yes king":
        print("You have chosen the legendary name 'Yes King'! Your hero shall be mighty!")
    stats = {"health": 10, "strength": 5, "luck": 1, "reset": 0}
    points_left = POINTS_TO_DISTRIBUTE
    while points_left > 0:
        print(f"\nYou have {points_left} points left to distribute.")
        stat_choice = questionary.select(
            "Choose a stat to increase:",
            choices=list(stats.keys())
        ).ask()
        if stat_choice == "reset":
            stats = {"health": 10, "strength": 5, "luck": 1, "reset": 0}
            points_left = POINTS_TO_DISTRIBUTE
            print("Stats have been reset.")
            continue
        increase_amount = int(questionary.text(f"How many points to add to {stat_choice}?").ask())
        if 0 < increase_amount <= points_left:
            stats[stat_choice] += increase_amount
            points_left -= increase_amount
        else:
            print("Invalid amount. Please try again.")
        
    hero_instance = hero.Hero(name, stats["health"], stats["strength"], stats["luck"])
    starting_weapon = choose_weapon()
    hero_instance.inventory.equip_item(starting_weapon, "right_hand")
    return hero_instance


def choose_weapon():
    choices = [
        questionary.Choice(
            title=f"{weapon.name} (Damage: {weapon.damage})",
            value=weapon
        )
        for weapon in weapons
    ]

    selected_weapon = questionary.select(
        "Choose your starting weapon:",
        choices=choices,
        style=questionary.Style([('selected', 'fg:#ff9d00 bold')])
    ).ask()

    return selected_weapon

if __name__ == "__main__":
    hero = create_hero()
    print(f"Hero {hero.name} created with {hero.health} health and {hero.strength} strength.")
    print("Is the hero alive?", hero.is_alive())
    print("Hero's inventory items:", hero.inventory.list_items())
    print("Hero's equipped items:", hero.inventory.list_equipped_items())
    print("Hero's effects:", hero.effects)
    input("Press Enter to continue...")
    # Further game logic can be added here