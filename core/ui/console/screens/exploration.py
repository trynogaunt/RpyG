from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import Quit

class ExplorationScreen(BaseConsoleScreen):
    def draw(self) -> None:
        self.rule()
        self.centered("Exploration Screen")
        self.rule()

    def ask(self):
        return self.choose([
            (self.t("ui.common.quit"), lambda: Quit())
        ])