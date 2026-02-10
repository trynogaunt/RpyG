from models.hero import Hero
from enum import Enum, auto
from world.build_world import load_world
from .enums import MainMenuOption, CreationMenuOption, AttributeType
from ui import toolkit as tk
# from game import combat
from events.response import GameResponse, ResponseType
from classes.interface_class import CharacterCreationState
from models.game_context import GameContext
from typing import TYPE_CHECKING
from time import sleep
import os
if TYPE_CHECKING:   
    from ui.ui_controller import UIController

class GameState(Enum):
    EXPLORING = auto()
    IN_BATTLE = auto()
    PAUSED = auto()
    MENU = auto()
    EXIT = auto()
    MAIN_MENU = auto()
    CHARACTER_CREATION = auto()


class Game:
    def __init__(self, ui: "UIController", ctx: GameContext):
        self.ui = ui
        self.hero = None
        self.state = GameState.MAIN_MENU
        self.was_loaded = False
        self.world = None
        self.last_message = ""
        self.current_combat = None
        self.discord_presence = None
        self.state_creation = CharacterCreationState()
        self.error_message = ""
        self.player_choice = None
        self.ctx = ctx

    def run(self):
        while (
            self.hero is None or self.hero.is_alive() and self.state != GameState.EXIT
        ):
            if self.discord_presence:
                self.discord_presence.update(self)
            match self.state:
                case GameState.MAIN_MENU:
                    self.handle_main_menu()
                case GameState.CHARACTER_CREATION:
                    self.handle_character_creation()
                case GameState.MENU:
                    self.handle_menu()
                case GameState.EXPLORING:
                    self.handle_exploration()
                case GameState.IN_BATTLE:
                    self.handle_combat()
                case GameState.PAUSED:
                    self.handle_pause()
                case GameState.MENU:
                    self.handle_menu()
                case GameState.EXIT:
                    self.handle_exit()

    def handle_main_menu(self):

        response = GameResponse(
            message="", type=ResponseType.MAIN_MENU, payload={"type": "splash_screen"}
        )
        self.ui.render(response)
        choice = self.ui.choose("", [(self.ctx.t("ui.main_menu.choose.start_game"), MainMenuOption.NEW_GAME.value), (self.ctx.t("ui.main_menu.choose.load_game"), MainMenuOption.LOAD_GAME.value), (self.ctx.t("ui.main_menu.choose.exit"), MainMenuOption.EXIT.value)])
        if choice == MainMenuOption.NEW_GAME.value:
            self.state = GameState.CHARACTER_CREATION
        elif choice == MainMenuOption.LOAD_GAME.value:
            # self.load("savefile.sav")
            self.state = GameState.EXPLORING
        elif choice == MainMenuOption.EXIT.value:
            self.state = GameState.EXIT

    def handle_character_creation(self):
        response = self.build_character_creation_response()
        self.ui.render(response)

        if self.state_creation.step == 1:
            name = self.ui.ask_text(self.ctx.t("ui.creation.name_prompt"))
            if name:
                self.state_creation.name = name
                self.state_creation.step = 2
            else:
                self.state_creation.error = self.ctx.t("ui.creation.name_error")
        elif self.state_creation.step == 2:
            choice = self.ui.choose(
                self.ctx.t("ui.creation.stats.prompt.attribute"),
                [
                    (f"{self.ctx.t('ui.creation.stats.health')}: {self.state_creation.health}", AttributeType.HEALTH.value),
                    (f"{self.ctx.t('ui.creation.stats.strength')}: {self.state_creation.strength}", AttributeType.STRENGTH.value),
                    (f"{self.ctx.t('ui.creation.stats.speed')}: {self.state_creation.speed}", AttributeType.SPEED.value),
                    (f"{self.ctx.t('ui.creation.stats.luck')}: {self.state_creation.luck}", AttributeType.LUCK.value),
                ]
            )
            if choice:
                match choice:
                    case AttributeType.HEALTH.value:
                        if self.state_creation.points_to_spend > 0:
                            self.state_creation.health += 1
                            self.state_creation.points_to_spend -= 1
                        else:
                            self.state_creation.error = self.ctx.t("ui.creation.stats.prompt.no_points")
                    case AttributeType.STRENGTH.value:
                        if self.state_creation.points_to_spend > 0:
                            self.state_creation.strength += 1
                            self.state_creation.points_to_spend -= 1
                        else:
                            self.state_creation.error = self.ctx.t("ui.creation.stats.prompt.no_points")
                    case AttributeType.SPEED.value:
                        if self.state_creation.points_to_spend > 0:
                            self.state_creation.speed += 1
                            self.state_creation.points_to_spend -= 1
                        else:
                            self.state_creation.error = self.ctx.t("ui.creation.stats.prompt.no_points")
                    case AttributeType.LUCK.value:
                        if self.state_creation.points_to_spend > 0:
                            self.state_creation.luck += 1
                            self.state_creation.points_to_spend -= 1
                        else:
                            self.state_creation.error = self.ctx.t("ui.creation.stats.prompt.no_points")
     
            if self.state_creation.points_to_spend == 0:
                self.state_creation.step = 3
        elif self.state_creation.step == 3:
            choice = self.ui.confirm(self.ctx.t("ui.creation.confirmation_prompt").format(name=self.state_creation.name, health=self.state_creation.health, strength=self.state_creation.strength, speed=self.state_creation.speed, luck=self.state_creation.luck))
            if choice:
                self.hero = self.build_hero_from_creation_state()
                self.build_world()
                self.state = GameState.EXPLORING
            else:
                self.state_creation.step = 1  # Go back to the beginning of character creation
                self.state_creation.points_to_spend = 5
                self.state_creation.health = 10
                self.state_creation.strength = 1
                self.state_creation.luck = 0
                self.state_creation.speed = 1
                self.state_creation.error = None

    def handle_exploration(self):
        response = GameResponse(
                message="", 
                type=ResponseType.EXPLORATION,
                payload={"room": self.hero.current_room }
        )
        choice_list = ["Move", "Look Around", "Inventory", "Exit"]
        while self.state == GameState.EXPLORING:
            if self.discord_presence:
                self.discord_presence.update(self)
            self.ui.render(response)
            if response.type == ResponseType.EXPLORATION:
                choice_list = ["Move", "Look Around", "Inventory", "Exit"]
            elif response.type == ResponseType.INVENTORY:
                choice_list = ["Use Item", "Equip Item", "Back to Exploration"]
            choice = self.ui.choose("What do you want to do?", choice_list)
            if choice == "Move":
                directions = list(self.hero.current_room.exits.keys())
                direction = self.ui.choose("Choose a direction to move:", directions)
                response = self.move_hero(direction)
            elif choice == "Look Around":
                response = GameResponse(
                    message=self.hero.current_room.describe(),
                    type=ResponseType.EXPLORATION,
                    payload={"room": self.hero.current_room}
                )
            elif choice == "Inventory":
                response = self.handle_inventory()
            elif choice == "Use Item":
                pass
            elif choice == "Equip Item":
                pass
            elif choice == "Back to Exploration":
                response = GameResponse(
                    message="",
                    type=ResponseType.EXPLORATION,
                    payload={"room": self.hero.current_room}
                )

            elif choice == "Exit":
                self.state = GameState.MAIN_MENU
                break
            
    def handle_combat(self):
        # ombat = combat.Combat(self.hero, self.hero.current_room.get_enemies())
        # self.current_combat = combat
        # combat.run()
        pass

    def handle_pause(self):
        pass

    def handle_exit(self):
        print(self.ctx.t("ui.main_menu.exit_message"), width=self.ui.width, border_char=" ")
        sleep(2)
        os._exit(0)

    def handle_menu(self):
        pass

    def handle_inventory(self) -> GameResponse:
        items = self.hero.inventory.list_items()
        equipped = self.hero.inventory.list_all_slots()
        response = GameResponse(
            message="", type=ResponseType.INVENTORY, payload={"equipped": equipped, "items": items, "gold": self.hero.gold}
        )
        return response
    
    def load(self, save_file: str):
        self.was_loaded = True
        pass

    def move_hero(self, direction) -> GameResponse:
        if self.hero.current_room and direction in self.hero.current_room.exits:
            if self.hero.current_room.exits[direction] is None:
                return GameResponse(
                    message=f"You cannot go {direction} from here.",
                    type=ResponseType.MOVE_BLOCKED,
                )
            else:
                new_room = self.hero.current_room.exits[direction]
                return self.change_room(new_room)
        else:
            return GameResponse(
                message=f"There is no exit to the {direction}.",
                type=ResponseType.MOVE_BLOCKED,
            )

    def change_room(self, new_room) -> GameResponse:
        if new_room["type"] == "room":
            self.hero.current_room = self.hero.current_zone.get_room_by_id(new_room["target"])
        elif new_room["type"] == "zone":
            self.hero.current_zone = self.world.get_zone(new_room["target"])
            self.hero.current_room = self.hero.current_zone.get_room_by_id(new_room["entry_room_id"])
            
        response = GameResponse(
            message=f"You move to {self.hero.current_room.name}.",
            type=ResponseType.ROOM_ENTERED,
            tags=["move", "room_change"],
            payload={
                "room": self.hero.current_room,
            },
        )
        return response

    def build_character_creation_response(self) -> GameResponse:
        state = self.state_creation
        if state.step == 1:
            msg = self.ctx.t("ui.creation.name_prompt")
        elif state.step == 2:
            if state.points_to_spend < 2:
                msg = self.ctx.t("ui.creation.stats.prompt.count.one").format(count=state.points_to_spend)
            else:
                msg = self.ctx.t("ui.creation.stats.prompt.count.other").format(count=state.points_to_spend)
        else:
            msg = "Character Creation"

        payload = {
            "character_name": state.name,
            "step": state.step,
            "available_points": state.points_to_spend,
            "stats_names": {
                "health": self.ctx.t("ui.creation.stats.health"),
                "strength": self.ctx.t("ui.creation.stats.strength"),
                "speed": self.ctx.t("ui.creation.stats.speed"),
                "luck": self.ctx.t("ui.creation.stats.luck"),
            },
            "character_stats": {
                "health": state.health,
                "strength": state.strength,
                "luck": state.luck,
                "speed": state.speed,
            },
            "stats_description": {
                "health": self.ctx.t("ui.creation.stats.health_desc"),
                "strength": self.ctx.t("ui.creation.stats.strength_desc"),
                "speed": self.ctx.t("ui.creation.stats.speed_desc"),
                "luck": self.ctx.t("ui.creation.stats.luck_desc"),
            },
            "error": state.error,
        }
        state.error = ""
        return GameResponse(
            message=msg, type=ResponseType.CHARACTER_CREATION, payload=payload
        )

    def build_hero_from_creation_state(self) -> Hero:
        state = self.state_creation
        hero = Hero(
            name=state.name,
            health=state.health,
            strength=state.strength,
            luck=state.luck,
            speed=state.speed,
        )
        return hero

    def build_world(self):
        self.world = load_world("world/zones")
        self.hero.current_zone = self.world.get_world_starting_zone()
        self.hero.current_room = self.world.get_world_starting_room()
    