import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.ui_controller import UIController
from events.response import GameResponse, ResponseType

def test_main_menu_render():
    response = GameResponse(
        type=ResponseType.MAIN_MENU,
        payload={},
        message=""
    )
    ui_controller = UIController()
    lines = ui_controller.render(response)
    
    assert any("R P y G  -  L E G A C Y" in line for line in lines), "Header not found in main menu render."
    assert any("In a world where dragons roam the skies" in line for line in lines), "Intro text not found in main menu render."
    assert any("Version 0.1 - Early Access" in line for line in lines), "Version info not found in main menu render."
    print("Main menu render test passed.")
    

if __name__ == "__main__":
    test_main_menu_render()