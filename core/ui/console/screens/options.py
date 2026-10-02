from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import Quit, NewGame, LoadGame, OpenSlots, Options
from core.ui.console import colors


class OptionsScreen(BaseConsoleScreen):
    def draw(self):
        self.rule()
        print(f"| {self.t('ui.options.title').center(self.width - 4)} |")
        self.rule()
        print()
        self.draw_splash()
        self.centered(self.t("ui.options.tagline"), colors.LIGHT_GRAY)
        self.box(
            [self.t("ui.options.lore"), "", ""],
            footer=self.t("ui.options.version"),
            footer_code=colors.LIGHT_GRAY,
        )
    print()

    def ask(self):
        return self.choose([
            (self.t("ui.options.new_game"), NewGame()),
            (self.t("ui.options.load_game"), OpenSlots(mode="load")),
            (self.t("ui.options.options"), Options()),
            (self.t("ui.options.quit"), Quit()),
        ])
        def ask(self):
            options = [
                (self.t("ui.options.new_game"), NewGame()),
                (self.t("ui.options.load_game"), OpenSlots(mode="load")),
                (self.t("ui.options.quit"), Quit())
            ]
            return self.choose(options)