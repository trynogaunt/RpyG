from creation import create_hero
from classes.ennemy import Enemy
from ui_console import splash, main_menu
import combat
import questionary
import game_logic
from classes import room

def main():
    
    splash()
    print("")
    choice = main_menu()
    if choice == "exit":
        print("Thanks for playing!")
        return

    starting_room = create_map()
    hero = create_hero()
    if hero.current_room is None:
        hero.change_room(starting_room, cause="start")
    
    while hero.is_alive():
        if hero.current_room.enemies:
            enemy = hero.current_room.enemies[0]
            print(f"A wild {enemy.name} appears!")
            combat.run_combat(hero, enemy)
            if not hero.is_alive():
                print("Game Over!")
                break
            else:
                hero.current_room.enemies.remove(enemy)
        else:
            print(f"You are in the {hero.current_room.name}.")
            direction = questionary.select(
                "Where do you want to go?",
                choices=list(hero.current_room.exits.keys())
            ).ask()
            hero.move(direction)
        


  
def create_map():
    hall = room.Room("Hall", "A spacious hall with marble floors.")
    library = room.Room("Library", "A quiet library filled with books.")
    kitchen = room.Room("Kitchen", "A kitchen with a lingering aroma of spices.")

    room.connect(hall, library, "north", "south")
    room.connect(hall, kitchen, "east", "west")

    return hall  # Return the starting room
if __name__ == "__main__":
    main()
    