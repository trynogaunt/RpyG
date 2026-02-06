import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.ui_controller import UIController
from events.response import GameResponse, ResponseType

def test_room_render():
    response = GameResponse(
        type=ResponseType.EXPLORATION,
        payload={"room": type("Room", (), {"name": "Test Room", "description": "This is a test room.", "exits": {"North": None, "East": None}})()},
        message="Test message for the room screen."
    )
    ui_controller = UIController()
    lines = ui_controller.render(response)
    
    assert any("Test Room" in line for line in lines), "Room name not found in room screen render."
    assert any("This is a test room." in line for line in lines), "Room description not found in room screen render."
    assert any("Exits: North, East" in line for line in lines), "Room exits not found in room screen render."
    assert any("Test message for the room screen." in line for line in lines), "Room message not found in room screen render."
    print("Room screen render test passed.")
    

if __name__ == "__main__":
    test_room_render()