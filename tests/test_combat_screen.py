import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.ui_controller import UIController
from events.response import GameResponse, ResponseType

def test_combat_render():
    response = GameResponse(
        type=ResponseType.IN_COMBAT,
        payload={"hero": {"name": "Hero", "health": 100, "strength": 10, "speed": 5, "luck": 2},
                 "enemies": [{"name": "Goblin", "health": 30, "strength": 5, "speed": 3, "luck": 1}]},
        message=""
    )
    ui_controller = UIController()
    lines = ui_controller.render(response)
    
    assert any("Section en construction" in line for line in lines), "Header not found in combat screen render."
    print("Combat screen render test passed.")

if __name__ == "__main__":
    test_combat_render()
