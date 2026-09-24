from textual.screen import Screen
from textual.widgets import Static, OptionList
from textual.widgets.option_list import Option
from textual import on
from core.game.actions import NewGame, Quit

class CreationScreen(Screen):
    
    def compose(self):
        yield Static("Creation Menu")