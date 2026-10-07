from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import Quit, NewGame, LoadGame, OpenSlots, Options, ApplyUpdate
from core.ui.console import colors
from core.updater import UpdateState

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
        options = [
            (self.t("ui.main_menu.new_game"), NewGame()),
            (self.t("ui.main_menu.load_game"), OpenSlots(mode="load")),
            (self.t("ui.main_menu.options"), Options()),
        ]
        update = self.app.game.update
        if update is not None and update.state is UpdateState.AVAILABLE:
            options.append((self.t("ui.main_menu.update"), ApplyUpdate()))
        options.append((self.t("ui.main_menu.quit"), Quit()))
        return self.choose(options)