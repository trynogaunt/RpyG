from ui import toolkit as tk
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ui.ui_controller import UIController
    from events.response import GameResponse

def render(ui: "UIController", response: "GameResponse")-> List[str]:
    lines = []
    
    return lines