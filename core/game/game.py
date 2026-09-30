from core.enums import Screens
from core.game.I18n import Translation
from core.enums import Stat
from dataclasses import dataclass
from pathlib import Path
from core.game.response import GameResponse, Message
from core.game.actions import Action, NewGame, Quit, SetName, AllocatePoints, ConfirmCreation, Creation, Move, Explore, LoadGame, SaveGame
from core.enums import Direction
from core.game.creation import CreationState
from core.game.player import Player
from core.world.loader import World, RoomRef
from core.world.models import WorldState
from core.views.base_view import BaseView
from core.views.exploration_view import ExplorationView
from core.game.text_keys import room_key
from core.errors import InvalidSave
from core.game.snapshot import GameSnapshot, PlayerSnapshot

class Game:
    def __init__(self, world: World | None = None, world_state: WorldState | None = None):
        self.screen: Screens | None = None
        self.creation: CreationState | None = None
        self.player: Player | None = None
        self.world: World = world
        self.world_state: WorldState = world_state or WorldState()
        self._messages: list[Message] = []

    def start(self) -> GameResponse:
        print("Starting game...")
        self.screen = Screens.MAIN_MENU

        return GameResponse(screen=self.screen)
    
    def _move_player(self, direction: Direction) -> None:
        next_room = self.world.exit_from(self.player.location, direction)
        if next_room:
            self.player.location = next_room
    
    def _build_to_view(self) -> BaseView | None:
        match self.screen:
            case Screens.CREATION:
                return self.creation.to_view()
            case Screens.EXPLORATION:
                return self._exploration_to_view()
            case _:
                return None
       
    
    def _exploration_to_view(self) -> ExplorationView:
        current_room = self.world.get_room(self.player.location)
        return ExplorationView(
            zone_id = self.player.location.zone_id,
            room_id = self.player.location.room_id,
            room_description=current_room.description,
            can_move={direction: self.world.exit_from(self.player.location, direction) is not None for direction in Direction},
            player_summary=self.player.to_summary()
        )

    def _explore_current_room(self) -> None:
        current_room = self.world.get_room(self.player.location)

        return Message(key="look_around", text="<text.messages.look_around>")

    def snapshot(self) -> GameSnapshot:
        p = self.player
        return GameSnapshot(
            player=PlayerSnapshot(
                name=p.name,
                health=p.health,
                level=p.level,
                allocated=tuple(p.allocated.items()),
            ),
            location=p.location,
            world_state=self.world_state,
            explored=tuple(sorted(self.world_state.explored, key=lambda r: (r.zone_id, r.room_id))),
            messages=tuple(self._messages)
        )
    
    def restore(self, snap: GameSnapshot) -> None:
        if snap.location not in self.world:            # adapte à ton API de World
            raise InvalidSave(f"Salle inconnue : {snap.location}")

        player = Player(name=snap.player.name)
        player.level = snap.player.level
        player.allocated = dict(snap.player.allocated)
        if sum(player.allocated.values()) > player.total_points():   # règle à toi
            raise InvalidSave("Points alloués incohérents")
        player.health = min(snap.player.health, player.max_health)
        player.location = snap.location

        self.player = player
        self.world_state.explored = set(snap.explored)
        self.screen = Screens.EXPLORATION
    
    def load_game(self) -> None:
        # Implémentation de la logique de chargement de la sauvegarde
        try:
            with open("save_file.json", "r") as f:
                import json
                data = json.load(f)
            snapshot = decode(data)
            self.restore(snapshot)
        except (FileNotFoundError, InvalidSave, KeyError, ValueError) as e:
            self._messages.append(Message(key="load_error", text=f"Erreur lors du chargement de la sauvegarde : {e}"))
            self.screen = Screens.MAIN_MENU
            
    def handle_action(self, action: Action) -> GameResponse:
        self._messages.clear()
        match self.screen:
            case Screens.MAIN_MENU:
                self._handle_main_menu(action)
            case Screens.CREATION:
                self._handle_creation(action)
            case Screens.EXPLORATION:
                self._handle_exploration(action)
            case _:
                raise ValueError(f"Aucun handler pour l'écran : {self.screen}")
        view = self._build_to_view()
        return GameResponse(screen=self.screen, view=view, messages=tuple(self._messages))
    
    def _handle_main_menu(self, action: Action) -> None:
        match action:
            case NewGame():
                self.screen = Screens.CREATION
                self.creation = CreationState()
            case LoadGame():
                self.load_game()
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
            case Explore():
                ref = self.player.location
                self.world_state.explored.add(ref)
                if ref in self.world_state.explored:
                    self._messages.append(Message(key="ui.messages.already_explored"))
                else:
                    self.world_state.explored.add(ref)
                    self._messages.append(Message(
                        key=room_key(ref, "look_around"),
                        fallback_key="ui.messages.nothing_special",
                    ))
            case SaveGame():
                self.save_game()
            case Quit():
                self.screen = Screens.MAIN_MENU
            case _:
                raise ValueError(f"Action inconnue : {action!r} (écran : {self.screen})")
    
    def _handle_exit(self, action: Action) -> None:
        match action:
            case _:
                raise ValueError(f"Action inconnue : {action!r} (écran : {self.screen})")
