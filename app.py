from creation import create_hero
from classes.ennemy import Enemy
from splashes import splash
from menu import main_menu
import questionary

def main():
    
    splash()
    print("")
    choice = main_menu()
    if choice == "exit":
        print("Thanks for playing!")
        return

    hero = create_hero()

    print(f"Hero {hero.name} created with {hero.health} health and {hero.strength} strength.")
    goblin = Enemy("Goblin", health=8, strength=2)
    print(f"An enemy {goblin.name} appears with {goblin.health} health and {goblin.strength} strength.")
    while hero.is_alive() and goblin.is_alive():
        action = questionary.select(
            "What will you do?",
            choices=[
                "Attack",
                "View Status",
                "Use Item",
                "Quit Game"
            ]
        ).ask()

        if action == "Attack":
            result = hero.attack(goblin)
            print(f"{hero.name} dealt {result} damage to {goblin.name}!")
            if goblin.is_alive():
                enemy_result = goblin.attack(hero)
                print(f"{goblin.name} dealt {enemy_result} damage to {hero.name}!")
            else:
                print(f"{goblin.name} has been defeated!")
        elif action == "Use Item":
            if not hero.inventory.list_items():
                print("Your inventory is empty!")
                continue
            item_choices = [
                questionary.Choice(title=item.name, value=item)
                for item in hero.inventory.items
            ]
            selected_item = questionary.select(
                "Choose an item to use:",
                choices=item_choices
            ).ask()
            result = selected_item.use(hero)
            print(result)
        elif action == "View Status":
            print(f"{hero.name} - Health: {hero.health}, Strength: {hero.strength}")
            print(f"{goblin.name} - Health: {goblin.health}, Strength: {goblin.strength}")
        elif action == "Quit Game":
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()