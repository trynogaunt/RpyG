from creation import create_hero
from classes.ennemy import Enemy
from ui_console import splash, main_menu
import combat
import questionary

def main():
    
    splash()
    print("")
    choice = main_menu()
    if choice == "exit":
        print("Thanks for playing!")
        return

    hero = create_hero()
    enemy = Enemy("Goblin", health=20, strength=4)
    print(f"\nA wild {enemy.name} appears!")
    input("Press Enter to start combat...")
    combat.run_combat(hero, enemy)


  

if __name__ == "__main__":
    main()
    