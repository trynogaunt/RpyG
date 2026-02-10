from abstract_screen import AbstractScreen
from ui import toolkit as tk

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ui.ui_controller import UIController
    from events.response import GameResponse


class ErrorScreen(AbstractScreen):
    def render(self, ui:"UIController", response:"GameResponse")-> List[str]:
        lines = []
        
        return lines
    
    def display(self, lines: List[str]) -> None:
        print("\n".join(lines))