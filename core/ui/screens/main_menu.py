from importlib.metadata import version, PackageNotFoundError

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Center
from textual.widgets import Static, OptionList
from textual.widgets.option_list import Option

from core.game.actions import NewGame, Quit
from core.ui.logo import LETTERS  # dict {"R": "...", "P": "...", ...}
from core.ui.screens.base_screen import BaseScreen

def app_version()-> str:
    try:
        return version("rpyg")
    except PackageNotFoundError:
        return "unknown"

class MainMenuScreen(BaseScreen):

    def compose(self):
        yield Static(id="title-bar")
        with Horizontal(id="logo"):
            for letter, cls in (("R", "logo-a"), ("P", "logo-b"), ("Y", "logo-c"), ("G", "logo-d")):
                s = Static(LETTERS[letter], classes=f"logo-letter {cls}")
                s.styles.width = "auto"
                yield s
        yield Static(id="tagline")
        yield Static(id="lore", classes="panel")
        with Center():
            yield OptionList(id="menu")
    
    def on_mount(self) -> None:
            t = self.app.t
            self.query_one("#title-bar", Static).update(t("ui.main_menu.title"))
            self.query_one("#tagline", Static).update(t("ui.main_menu.tagline"))
            lore = self.query_one("#lore", Static)
            lore.update(t("ui.main_menu.lore"))
            lore.border_subtitle = t("ui.main_menu.version", version=app_version())

            menu = self.query_one("#menu", OptionList)
            menu.add_options([
                Option(t("ui.main_menu.new_game"), id="new_game"),
                Option(t("ui.main_menu.load_game"), id="load_game", disabled=True),
                Option(t("ui.main_menu.quit"), id="quit"),
            ])
            menu.focus()

    @on(OptionList.OptionSelected, "#menu")
    def on_menu_selected(self, event: OptionList.OptionSelected) -> None:
        match event.option.id:
            case "new_game":
                self.app.dispatch(NewGame())
            case "load_game":
                pass  # Implement load game functionality here
            case "quit":
                self.app.dispatch(Quit())