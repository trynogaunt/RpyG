from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import Quit, NewGame

class MainMenuScreen(BaseConsoleScreen):
    def draw(self) -> None:
        print("=== Main Menu ===")

    def ask(self):
        options = [
            (self.t("ui.main_menu.new_game"), NewGame()),
            (self.t("ui.main_menu.quit"), Quit())
        ]
        return self.choose(options)