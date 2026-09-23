from core.enums import Screen
from core.game.response import GameResponse
from core.game.actions import Action, NewGame, Quit

class Game:
    def __init__(self):
        self.screen: Screen | None = None
    
    def start(self) -> GameResponse:
        self.screen = Screen.MAIN_MENU

        return GameResponse(screen=self.screen)
    
    def handle_action(self, action: Action) -> GameResponse:

        match action:
            case NewGame() if self.screen is Screen.MAIN_MENU:
                self.screen = Screen.CREATION
            case NewGame():
                pass
            case Quit():
                self.screen = Screen.EXIT
            case _:
                raise ValueError(f"Action inconnue : {action!r} (écran : {self.screen})")
        return GameResponse(screen=self.screen)