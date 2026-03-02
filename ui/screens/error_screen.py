from ui.screens.abstract_screen import AbstractScreen
from ui import toolkit as tk

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ui.ui_controller import UIController
    from events.response import GameResponse


class ErrorScreen(AbstractScreen):
    def render(self, ui:"UIController", response:"GameResponse")-> List[str]:
        lines = []
        lines.append(tk.center_text("An error has occurred!"))
        return lines
    
    def display(self, lines: List[str]) -> None:
        print("\n".join(lines))
    
    def handle_input(self, ui:"UIController"):
        input("Press Enter to continue...")
    
    def actions(self):
        return []