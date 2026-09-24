from core.enums import Screens
from core.game.response import GameResponse
from core.game.actions import Action, NewGame, Quit, SetName, AllocatePoints, ConfirmCreation

class Game:
    def __init__(self):
        self.screen: Screens | None = None
    
    def start(self) -> GameResponse:
        print("Starting game...")
        self.screen = Screens.MAIN_MENU

        return GameResponse(screen=self.screen)
    
    def handle_action(self, action: Action) -> GameResponse:

        match action:
            case NewGame() if self.screen is Screens.MAIN_MENU:
                self.screen = Screens.CREATION
            case NewGame():
                pass
            case Quit():
                self.screen = Screens.EXIT
            case _:
                raise ValueError(f"Action inconnue : {action!r} (écran : {self.screen})")
        return GameResponse(screen=self.screen)