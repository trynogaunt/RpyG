from core.ui.screens.base_screen import BaseScreen
from textual.widgets import Static, OptionList
from textual.widgets.option_list import Option
from textual import on
from core.game.actions import NewGame, Quit

class ExplorationScreen(BaseScreen):
    def compose(self):
        yield Static("Exploration Screen")