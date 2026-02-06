import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.ui_controller import UIController
from events.response import GameResponse, ResponseType

def test_character_creation_render(character_name="", available_points=10, character_stats={"Health": 10, "Strength": 5, "Speed": 5, "Luck": 1}):
    response = GameResponse(
        type=ResponseType.CHARACTER_CREATION,
        payload={"step": 1, 
                 "character_name": character_name,
                 "available_points": available_points, 
                 "character_stats": character_stats,
                 "stats_description": {"Health": "Determines how much damage you can take.", "Strength": "Affects the damage you deal to enemies.", "Speed": "Influences your chances to dodge enemies and initiate the combat", "Luck": "Can affect various random outcomes in the game."}},
        message=""
    )
    ui_controller = UIController()
    lines = ui_controller.render(response)
    
    assert any("Character Creation" in line for line in lines), "Header not found in character creation render."
    assert any("Welcome to the character creation screen!" in line for line in lines), "Intro text not found in character creation render."
    assert any("1/3" in line for line in lines), "Step info not found in character creation render."
    print("Character creation render test passed.")
    

if __name__ == "__main__":
    test_character_creation_render("Hero", 15, {"Health": 12, "Strength": 7, "Speed": 6, "Luck": 2})