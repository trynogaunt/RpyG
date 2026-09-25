from core.enums import Screens
from core.game.response import GameResponse
from core.game.actions import Action, NewGame, Quit, SetName, AllocatePoints, ConfirmCreation, Creation, Move
from core.enums import Direction
from core.game.creation import CreationState
from core.game.player import Player
from core.world.loader import World, RoomRef

class Game:
    def __init__(self, world: World | None = None):
        self.screen: Screens | None = None
        self.creation: CreationState | None = None
        self.player: Player | None = None
        self.world: World | None = world
    
    def start(self) -> GameResponse:
        print("Starting game...")
        self.screen = Screens.MAIN_MENU

        return GameResponse(screen=self.screen)
    
    def _move_player(self, direction: Direction) -> None:
        if not self.player or not self.world:
            return
        next_room = self.world.exit_from(self.player.location, direction)
        if next_room:
            self.player.location = next_room
    
    def handle_action(self, action: Action) -> GameResponse:
        match self.screen:
            case Screens.MAIN_MENU:
                self._handle_main_menu(action)
            case Screens.CREATION:
                self._handle_creation(action)
            case Screens.EXPLORATION:
                self._handle_exploration(action)
            case _:
                raise ValueError(f"Aucun handler pour l'écran : {self.screen}")
        view = self.creation.to_view() if self.screen == Screens.CREATION else None
        return GameResponse(screen=self.screen, view=view)
    
    def _handle_main_menu(self, action: Action) -> None:
        match action:
            case NewGame():
                self.screen = Screens.CREATION
                self.creation = CreationState()
            case Quit():
                self.screen = Screens.EXIT
            case _:
                raise ValueError(f"Action inconnue : {action!r} (écran : {self.screen})")

    
    def _handle_creation(self, action: Action) -> None:
        match action:
            case SetName(name=name):
                self.creation.name = name.strip()
            case AllocatePoints(stat=stat, delta=1):
                if self.creation.can_add(stat):
                    self.creation.allocated_points[stat] += 1
            case AllocatePoints(stat=stat, delta=-1):
                if self.creation.can_remove(stat):
                    self.creation.allocated_points[stat] -= 1
            case ConfirmCreation():
                if self.creation.can_confirm():
                    self.player = Player(name=self.creation.name, allocated_points=self.creation.allocated_points, location=self.world.start)
                    self.creation = None
                    self.screen = Screens.EXPLORATION
            case NewGame() | Quit():
                pass
            case _:
                raise ValueError(f"Action inconnue : {action!r} (écran : {self.screen})")
    
    def _handle_exploration(self, action: Action) -> None:
        match action:       
            case Move(direction=direction):
                self._move_player(direction)
            case Quit():
                self.screen = Screens.MAIN_MENU
            case _:
                raise ValueError(f"Action inconnue : {action!r} (écran : {self.screen})")
    
    def _handle_exit(self, action: Action) -> None:
        match action:
            case _:
                raise ValueError(f"Action inconnue : {action!r} (écran : {self.screen})")
