from ui import toolkit as tk
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ui.ui_controller import UIController
    from events.response import GameResponse


def render(ui: "UIController", response: "GameResponse") -> List[str]:
    lines = []
    lines.extend(tk.header("Section en construction", ui.width, ui.border_char, ui.header_char))
    
    return lines
    
