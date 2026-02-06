import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.ui_controller import UIController
from events.response import GameResponse, ResponseType

def test_inventory_render():
    response = GameResponse(
        type=ResponseType.INVENTORY,
        payload={"golds": 150, "items": ["Sword", "Shield"], "equipped": {
            "left_hand": "Shield",
            "right_hand": None,
            "torso": None,
            "legs": None,
            "head": None,
            "feet": None
        }},
        message=""
    )
    ui_controller = UIController()
    lines = ui_controller.render(response)
    
    assert isinstance(lines, list), "Render should return a list of lines."
    assert len(lines) > 0, "Render should return at least one line."
    assert any("Gold" in line for line in lines), "Render should include gold information."
    assert any("Sword" in line for line in lines), "Render should include item information."
    assert any("Shield" in line for line in lines), "Render should include item information."
    print("Inventory render test passed.")
    
    return lines
if __name__ == "__main__":
    test_inventory_render()