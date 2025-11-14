from creation import create_hero
from classes.ennemy import Enemy
from ui_console import splash, main_menu
import combat
import questionary
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
    
        


  
def create_map():
    hall = room.Room("Hall", "A spacious hall with marble floors.")
    library = room.Room("Library", "A quiet library filled with books.")
    kitchen = room.Room("Kitchen", "A kitchen with a lingering aroma of spices.")

    room.connect(hall, library, "north", "south")
    room.connect(hall, kitchen, "east", "west")

    return hall  # Return the starting room
if __name__ == "__main__":
    main()
    