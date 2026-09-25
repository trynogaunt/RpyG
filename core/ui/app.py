from textual.app import App 
from textual.screen import Screen
from pathlib import Path

from core.game.response import GameResponse
from core.enums import Screens
from core.ui.screens.main_menu import MainMenuScreen
from core.ui.screens.creation import CreationScreen
from core.ui.screens.exploration import ExplorationScreen

class RpygApp(App):

    CSS_PATH = Path("rpyg.tcss")
    def __init__(self, game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game
        self.current_screen_id: int = None
        self.all_screens = {
            Screens.MAIN_MENU: MainMenuScreen,
            Screens.CREATION: CreationScreen,
            Screens.EXPLORATION: ExplorationScreen,
        }

    def build_screen(self, screen_id: Screens, view=None) -> Screen:
        screen_class = self.all_screens.get(screen_id)
        if screen_class:
            return screen_class(view=view)
        else:
            raise ValueError(f"No screen found for {screen_id}")

    def on_mount(self):
        response = self.game.start()
        self.current_screen_id = response.screen
        self.push_screen(self.build_screen(response.screen, response.view))

    def dispatch(self, action):
        response = self.game.handle_action(action)
        self.show(response)
    
    def show(self, response):
        if response.screen is Screens.EXIT:
            self.exit()
            return
        if response.screen is self.current_screen_id:
            self.screen.update_view(response.view)       
        else:
            self.current_screen_id = response.screen
            self.switch_screen(self.build_screen(response.screen, response.view))