from textual.app import App 
from textual.screen import Screen

from core.game.response import GameResponse
from core.enums import Screens
from core.ui.screens.main_menu import MainMenuScreen
from core.ui.screens.creation import CreationScreen

class RpygApp(App):
    def __init__(self, game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game
        self.current_screen = None
        self.all_screens = {
            Screens.MAIN_MENU: MainMenuScreen,
            Screens.CREATION: CreationScreen,
        }

    def build_screen(self, screen_id: Screens) -> Screen:
        screen_class = self.all_screens.get(screen_id)
        if screen_class:
            return screen_class()
        else:
            raise ValueError(f"No screen found for {screen_id}")

    def on_mount(self):
        response = self.game.start()
        self.push_screen(self.build_screen(response.screen))

    def dispatch(self, action):
        response = self.game.handle_action(action)
        self.show(response)
    
    def show(self, response: GameResponse):
        match response.screen:
            case Screens.EXIT:
                self.exit()
            case _:
                if self.current_screen == response.screen:
                    self.update_view()
                self.switch_screen(self.build_screen(response.screen))
                self.current_screen = response.screen