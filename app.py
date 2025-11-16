from ui.screens.main_menu_screen import splash, main_menu_choice
from ui.ui_controller import UIController

def main():
    ui = UIController(width=80, border_char="=", padding=2)
    splash_lines = splash()
    ui.render(splash_lines, tick_render=0.05)
    choice = main_menu_choice()
    if choice == "Start New Game":
        pass
    elif choice == "Settings":
        pass
    elif choice == "Load Game":
        pass
    elif choice == "Exit":
        print("Exiting the game. Goodbye!")


    
if __name__ == "__main__":
    main()
    