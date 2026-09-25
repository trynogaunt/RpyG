from core.ui.screens.base_screen import BaseScreen
from textual.widgets import Static, OptionList
from textual.widgets.option_list import Option
from textual import on
from core.game.actions import NewGame, Quit
from core.views.exploration_view import ExplorationView

class ExplorationScreen(BaseScreen):
    def compose(self):
        yield Static("", id="zone_name")
        yield Static("", id="room_name")
        yield Static("", id="room_description")
    
    def update_view(self, view: ExplorationView):
        self.query_one("#zone_name", Static).update(view.zone_name)
        self.query_one("#room_name", Static).update(view.room_name)
        self.query_one("#room_description", Static).update(view.room_description)