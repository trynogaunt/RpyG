from models.hero import Hero
from enum import Enum, auto
from world.build_world import load_world
from enums import MainMenuOption, CreationMenuOption, AttributeType
# from game import combat
from events.response import GameResponse, ResponseType
from classes.interface_class import CharacterCreationState
from typing import TYPE_CHECKING
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
    def __init__(self, ui: "UIController"):
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
                    break

    def handle_main_menu(self):

        response = GameResponse(
            message="", type=ResponseType.MAIN_MENU, payload={"type": "splash_screen"}
        )
        self.ui.render(response)
        choice = self.ui.choose("", [MainMenuOption.NEW_GAME.value, MainMenuOption.LOAD_GAME.value, MainMenuOption.EXIT.value])
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

        if self.state_creation.step == "name":
            self.state_creation.name = self.ui.ask_text("Enter your character's name:")
            if self.state_creation.name.strip() == "":
                self.state_creation.error = "Name cannot be empty."
            else:
                self.state_creation.step = "attributes"
        elif self.state_creation.step == "attributes" and self.state_creation.points_to_spend > 0:
            attr = response.payload["attributes"]
            choices = [f"{a['label']}: {a['value']}" for a in attr]
            choices.append(CreationMenuOption.FINISH.value)
            choice = self.ui.choose(
                f"Distribute your attribute points. Points left: {self.state_creation.points_to_spend}",
                choices,
            )
            attr_id = choice.split(":")[0].lower()

            if choice.startswith(CreationMenuOption.FINISH.value):
                if self.state_creation.points_to_spend == 0:
                    self.state_creation.step = "summary"
                else:
                    self.ui.text_block("You still have points to spend!", wrap=True)

                    choice = self.ui.confirm(
                        "Are you sure you want to finish?"
                    )
                    if choice:
                        self.state_creation.step = "summary"
            elif choice.startswith(AttributeType.HEALTH.value):
                self.state_creation.health += 5
                self.state_creation.points_to_spend -= 1
            elif choice.startswith(AttributeType.STRENGTH.value):
                self.state_creation.strength += 1
                self.state_creation.points_to_spend -= 1
            elif choice.startswith(AttributeType.LUCK.value):
                self.state_creation.luck += 1
                self.state_creation.points_to_spend -= 1
            elif choice.startswith(AttributeType.SPEED.value):
                self.state_creation.speed += 1
                self.state_creation.points_to_spend -= 1
            
            if self.state_creation.points_to_spend <= 0:
                self.state_creation.points_to_spend = 0
                self.state_creation.step = "summary"
        elif self.state_creation.step == "summary":
            confirm = self.ui.confirm("Confirm your character ?")
            if confirm:
                self.hero = Hero(
                    name=self.state_creation.name,
                    health=self.state_creation.health,
                    strength=self.state_creation.strength,
                    luck=self.state_creation.luck,
                    speed=self.state_creation.speed,
                )
                self.build_world()
                self.state = GameState.EXPLORING
            else:
                self.state_creation = CharacterCreationState()

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
        self.ui.text_block("Thank you for playing!", wrap=True)
        return
        self.state = GameState.EXIT

    def handle_menu(self):
        pass

    def handle_inventory(self) -> GameResponse:
        items = self.hero.inventory.list_items()
        equipped = self.hero.inventory.list_equipped_items()
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
        if state.step == "name":
            msg = "Enter your character's name:"
        elif state.step == "attributes":
            msg = f"Distribute your attribute points. Points left: {state.points_to_spend}"
        else:
            msg = "Character Creation"

        payload = {
            "name": state.name,
            "step": state.step,
            "attributes": [
                {"id": "health", "value": state.health, "label": "Health"},
                {"id": "strength", "value": state.strength, "label": "Strength"},
                {"id": "luck", "value": state.luck, "label": "Luck"},
                {"id": "speed", "value": state.speed, "label": "Speed"},
            ],
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
    