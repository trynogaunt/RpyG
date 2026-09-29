from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import Quit, NewGame
from core.ui.console import colors


class MainMenuScreen(BaseConsoleScreen):
    def draw(self):
        self.rule()
        print(f"| {self.t('ui.main_menu.title').center(self.width - 4)} |")
        self.rule()
        print()
        self.draw_splash()
        self.centered(self.t("ui.main_menu.tagline"), colors.LIGHT_GRAY)
        self.box(
            [self.t("ui.main_menu.lore"), "", ""],
            footer=self.t("ui.main_menu.version"),
            footer_code=colors.LIGHT_GRAY,
        )
    print()

    def ask(self):
        return self.choose([
            (self.t("ui.main_menu.new_game"), NewGame()),
            (self.t("ui.main_menu.quit"), Quit()),
        ])
        def ask(self):
            options = [
                (self.t("ui.main_menu.new_game"), NewGame()),
                (self.t("ui.main_menu.quit"), Quit())
            ]
            return self.choose(options)