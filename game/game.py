from models.hero import Hero
from enum import Enum, auto
from world_folder.world import WorldGraph, ProcGenerator
from world_folder.room import load_room_templates
from pathlib import Path

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
        self.current_room_id = None
        self.discord_presence = None
        self.state_creation = CharacterCreationState()
        self.error_message = ""
        self.player_choice = None
    
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
            if self.state_creation.name.strip() == "":
                self.state_creation.error = "Name cannot be empty."
            else:
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
                self.new_game()
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
                DIRECTIONS = ["North", "South", "East", "West", "Cancel"]
                direction = self.ui.choose("Choose a direction to move:", DIRECTIONS)
                if direction != "Cancel":
                    response = self.move_hero(direction)
            elif choice == "Look Around":
                response = GameResponse(
                    message=self.hero.current_room.get_description,
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
        if self.hero.current_room and direction in self.hero.current_room.neighbors:
            if self.hero.current_room.neighbors[direction] is None:
                return GameResponse(
                    message=f"You cannot go {direction} from here.",   
                    type=ResponseType.EXPLORATION,
                    tags=["move_blocked"],
                    payload={
                        "room": self.hero.current_room,
                    }, 
                )
            else:
                new_room = self.hero.current_room.neighbors[direction]
                return self.change_room(new_room)
        else:
            return GameResponse(
                message=f"There is no exit to the {direction}.",
                type=ResponseType.EXPLORATION,
                tags=["move_blocked"],
                payload={
                    "room": self.hero.current_room,
                },
            )

    def change_room(self, new_room) -> GameResponse:
        new_room_instance = self.world.get_room_by_id(new_room)
        self.hero.current_room = new_room_instance
        self.hero.visited_rooms.add(new_room_instance.instance_id)
        new_room_instance.marked_visited()
            
        response = GameResponse(
            message=f"You move to {self.hero.current_room.get_label}.",
            type=ResponseType.EXPLORATION,
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

    def new_game(self, seed: int = None):
        self.world = WorldGraph(seed=seed)
        room_templates = load_room_templates(Path("world_folder/datas/room_templates.json"))
        proc_gen = ProcGenerator(room_templates, self.world)
        
        spawn_id = proc_gen.create_spawn("village_square", position=(0,0))
        
        DIRECTIONS = {
            "North": (0, 1),
            "South": (0, -1),
            "East": (1, 0),
            "West": (-1, 0),
        }
        for _ in range(300):
            parent_id = self.world.rng.choice(list(self.world.rooms.keys()))
            direction, offset = self.world.rng.choice(list(DIRECTIONS.items()))
            proc_gen.generate_neighbor(parent_id, direction, offset)
        
        print(f"Generated world with {len(self.world.rooms)} rooms.")
        self.current_room_id = spawn_id
        self.hero.current_room = self.world.get_room_by_id(spawn_id)
        self.hero.current_room.marked_visited()
        self.hero.visited_rooms.add(spawn_id)
    