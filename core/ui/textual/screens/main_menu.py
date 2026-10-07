from importlib.metadata import version, PackageNotFoundError
from core.enums import Screens
from core.updater import UpdateState

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Center
from textual.widgets import Static, OptionList
from textual.widgets.option_list import Option
from rich.text import Text
from core.ui import splash

from core.game.actions import NewGame, Quit, OpenSlots, Options, ApplyUpdate
from core.ui.textual.logo import LETTERS  # dict {"R": "...", "P": "...", ...}
from core.ui.textual.screens.base_screen import BaseScreen
from textual.widgets import Static
from core.ui.textual.widgets.splash import build_splash

LETTER_STYLES = ["#c5cdd9", "#ffb000", "#ffb000", "#c5cdd9"] 

def app_version()-> str:
    try:
        return version("rpyg")
    except PackageNotFoundError:
        return "unknown"

class MainMenuScreen(BaseScreen):

    def compose(self):
        yield Static(id="title-bar")
        with Center():
            yield Static(build_splash(), id="splash")
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

            menu_options = [
                Option(t("ui.main_menu.new_game"), id="new_game"),
                Option(t("ui.main_menu.load_game"), id="load_game"),
                Option(t("ui.main_menu.options"), id="settings"),
            ]

            update = self.app.game.update
            if update is not None and update.state is UpdateState.AVAILABLE:
                menu_options.append(Option(t("ui.main_menu.update"), id="update"))
            
            menu_options.append(Option(t("ui.main_menu.quit"), id="quit"))
            menu.add_options(menu_options)
            menu.focus()

    @on(OptionList.OptionSelected, "#menu")
    def on_menu_selected(self, event: OptionList.OptionSelected) -> None:
        match event.option.id:
            case "new_game":
                self.app.dispatch(NewGame())
            case "load_game":
                self.app.dispatch(OpenSlots(mode="load"))
            case "settings":
                self.app.dispatch(Options())
            case "update":
                self.app.dispatch(ApplyUpdate())
            case "quit":
                self.app.dispatch(Quit())