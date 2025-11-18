from models.hero import Hero
from enum import Enum, auto
from world.build_world import build_world

# from game import combat
from events.response import GameResponse, ResponseType
from classes.interface_class import CharacterCreationState


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

    def run(self):
        while (
            self.hero == None or self.hero.is_alive() and self.state != GameState.EXIT
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
        choice = self.ui.choose("", ["Start New Game", "Load Game", "Exit"])
        if choice == "Start New Game":
            self.state = GameState.CHARACTER_CREATION
        elif choice == "Load Game":
            # self.load("savefile.sav")
            self.state = GameState.EXPLORING
        elif choice == "Exit":
            self.state = GameState.EXIT

    def handle_character_creation(self):
        response = self.build_character_creation_response()
        self.ui.render(response)

        if self.state_creation.step == "name":
            self.state_creation.name = self.ui.ask_text("Enter your character's name:")
            self.state_creation.step = "attributes"
        elif self.state_creation.step == "attributes" and self.state_creation.points_to_spend > 0:
            attr = response.payload["attributes"]
            choices = [f"{a['label']}: {a['value']}" for a in attr]
            choices.append("Finish Creation")
            choice = self.ui.choose(
                f"Distribute your attribute points. Points left: {self.state_creation.points_to_spend}",
                choices,
            )
            attr_id = choice.split(":")[0].lower()

            if choice.startswith("Finish Creation"):
                if self.state_creation.points_to_spend == 0:
                    self.state_creation.step = "summary"
                else:
                    self.ui.text_block("You still have points to spend!", wrap=True)

                    choice = self.ui.confirm(
                        "Are you sure you want to finish?"
                    )
                    if choice:
                        self.state_creation.step = "summary"
            elif choice.startswith("Health"):
                self.state_creation.health += 5
                self.state_creation.points_to_spend -= 1
            elif choice.startswith("Strength"):
                self.state_creation.strength += 1
                self.state_creation.points_to_spend -= 1
            elif choice.startswith("Luck"):
                self.state_creation.luck += 1
                self.state_creation.points_to_spend -= 1
            elif choice.startswith("Speed"):
                self.state_creation.speed += 1
                self.state_creation.points_to_spend -= 1
            
            if self.state_creation.points_to_spend <= 0:
                self.state_creation.points_to_spend = 0
                self.state_creation.step = "summary"
        elif self.state_creation.step == "summary":
            confirm = self.ui.confirm(f"Confirm your character ?")
            if confirm:
                self.hero = Hero(
                    name=self.state_creation.name,
                    health=self.state_creation.health,
                    strength=self.state_creation.strength,
                    luck=self.state_creation.luck,
                    speed=self.state_creation.speed,
                )
                self.world = build_world()
                self.hero.current_room = self.world.starting_room
                self.state = GameState.EXPLORING
            else:
                self.state_creation = CharacterCreationState()

    def handle_exploration(self):
        if choice == "Look Around":
            pass
        elif choice == "Move":
            move_response = self.ui.present_choices(
                "Choose a direction to move:",
                move_choices_section(self.hero.current_room),
            )
            if move_response in self.hero.current_room.exits:
                response = self.move_hero(move_response)
                self.ui.text_block(response.message, wrap=True)
                if "enemies" in response.payload and response.payload["enemies"]:
                    self.ui.text_block("You encounter enemies!", wrap=True)
                    self.state = GameState.IN_BATTLE
            else:
                self.ui.text_block("Invalid direction.", wrap=True)
        elif choice == "Inventory":
            self.ui.text_block("You check your inventory.", wrap=True)
        elif choice == "Pause Game":
            self.state = GameState.PAUSED
        elif choice == "Exit Game":
            self.state = GameState.EXIT

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
                return change_room(self, new_room)
        else:
            return GameResponse(
                message=f"There is no exit to the {direction}.",
                type=ResponseType.MOVE_BLOCKED,
            )

    def change_room(self, new_room) -> GameResponse:
        old_room = self.hero.current_room
        self.hero.current_room = new_room
        response = GameResponse(
            message=f"You move from {old_room.name} to {new_room.name}.",
            type=ResponseType.ROOM_ENTERED,
            tags=["move", "room_change"],
            payload={
                "from": old_room,
                "to": new_room,
                "enemies": new_room.get_enemies(),
                "exits": new_room.exits,
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
        }
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
