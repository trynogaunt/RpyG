from ui.ui_controller import UIController 
from game.combat import Combat

UI = UIController()

def show_combat_ui(combat: Combat, actions):
    UI.clear()