from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import CloseCatalog
from core.ui.console import colors
from core.updater import UpdateState
from core.version import __version__

class CatalogScreen(BaseConsoleScreen):
    def draw(self):
        self.rule()
        print(f"| {self.t('ui.dev_mode.title').center(self.width - 4)} |")
        self.rule()
        print()
        print("ici en dev mode")

    def ask(self):
        options = [
            (self.t("ui.catalog.close"), CloseCatalog())
        ]

        return self.choose(options)