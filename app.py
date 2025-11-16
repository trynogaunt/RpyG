from ui.screens.main_menu_screen import splash, main_menu_choice
from ui.ui_controller import UIController
from classes.hero import Hero
from game import creation_flow, game
import questionary


def main():
    hero = None
    ui = UIController(width=80, border_char="=", padding=2)
    splash_lines = splash()
    ui.render(splash_lines, tick_render=0.05)
    choice = main_menu_choice()
    if choice == "Start New Game":
        hero = creation_flow.create_character(ui)
    elif choice == "Settings":
        pass
    elif choice == "Load Game":
        pass
    elif choice == "Exit":
        print("Exiting the game. Goodbye!")

    if hero:
        start_adventure = questionary.confirm("Start your adventure now?").ask()
    else:
        print("No character created.")

    if hero and start_adventure:
        game_instance = game.Game(ui, hero)
        game_instance.run()
if __name__ == "__main__":
    main()
    