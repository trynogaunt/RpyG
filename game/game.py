from classes.hero import Hero
from classes.room import Room
from enum import Enum, auto
from ui.screens.room_screen import build_room_screen, choices_section as room_choices_section

class GameState(Enum):
    EXPLORING = auto()
    IN_BATTLE = auto()
    PAUSED = auto()
    MENU = auto()
    EXIT = auto()
class Game:
    def __init__(self, ui: "UIController", hero: Hero):
        self.ui = ui
        self.hero = hero
        self.state = GameState.EXPLORING
        self.actions = []
        self.was_loaded = False

    def run(self):
        if self.was_loaded:
            self.ui.text_block(f"Welcome back, {self.hero.name}! Resuming your adventure...", wrap=True)
        else:
            self.ui.text_block(f"Welcome, {self.hero.name}! Your adventure begins now...", wrap=True)
            room = Room("Starting Room", "You find yourself in a dimly lit room with stone walls.")
            self.hero.current_room = room
        while self.hero.is_alive() and self.state != GameState.EXIT:
            match self.state:
                case GameState.EXPLORING:
                    self.actions = ["Look Around", "Move", "Inventory", "Pause Game", "Exit Game"]
                    self.handle_exploration()
                case GameState.IN_BATTLE:
                    self.ui.text_block("You are in battle!", wrap=True)
                    self.handle_combat()
                case GameState.PAUSED:
                    self.ui.text_block("Game is paused.", wrap=True)
                    self.handle_pause()
                case GameState.MENU:
                    self.ui.text_block("In game menu.", wrap=True)
                    self.handle_menu()
                case GameState.EXIT:
                    self.ui.text_block("Exiting the game. Goodbye!", wrap=True)
                    self.handle_exit()
                    break
                
    def handle_exploration(self):
        room = self.hero.current_room
        if room is None:
            self.ui.text_block("You are nowhere. The game seems to be broken.", wrap=True)
            self.state = GameState.EXIT
            return
        self.ui.render(build_room_screen(self.ui, self.hero, actions=self.actions))
        choice = room_choices_section(self.actions)
        if choice == "Look Around":
            self.ui.text_block(f"You look around the room: {room.description}", wrap=True)
        elif choice == "Move":
            direction = questionary.text("Enter direction to move (e.g., north, south):").ask()
            if self.hero.move(direction):
                self.ui.text_block(f"You move {direction}.", wrap=True)
            else:
                self.ui.text_block("You can't move in that direction.", wrap=True)
        elif choice == "Inventory":
            self.ui.text_block("You check your inventory.", wrap=True)
        elif choice == "Pause Game":
            self.state = GameState.PAUSED
        elif choice == "Exit Game":
            self.state = GameState.EXIT
            
    def handle_combat(self):
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