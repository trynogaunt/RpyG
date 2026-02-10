from ui import toolkit as tk
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ui.ui_controller import UIController
    from events.response import GameResponse

class AbstractScreen(ABC):
    
    @abstractmethod
    def render(self, ui: "UIController", response:"GameResponse") -> List[str]:
        """
        Render the screen based on the provided GameResponse and return a list of strings to display.
        """
        raise NotImplementedError("Subclasses must implement the render method.")
    
    @abstractmethod
    def display(self, lines:List[str]) -> None:
        """
        Display lines on screen
        """
        print("No screen here")
    
    @abstractmethod
    def handle_input(self, ui):
        pass
    
    @abstractmethod
    def actions(self):
        pass
    
        
    