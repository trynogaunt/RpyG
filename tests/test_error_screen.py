import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.ui_controller import UIController
from events.response import GameResponse, ResponseType
from models.game_context import GameContext
from ui.screens.error_screen import ErrorScreen

def test_error_screen_render():
    response = GameResponse(
        type=ResponseType.ERROR,
        payload={},
        message=""
    )
    mock_settings = {
        "text_width": 80,
        "screen_width": 100,
        "screen_height": 30
    }
    game_context = GameContext()
    ui_controller = UIController(game_context)
    error_screen = ErrorScreen()
    lines = error_screen.render(ui_controller, response)
    
    assert any("An error has occurred!" in line for line in lines), "Error message not found in error screen render."
    print("Error screen render test passed.")
    
if __name__ == "__main__":
    test_error_screen_render()