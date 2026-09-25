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
    
    def update_view(self, view: ExplorationView):
        self.query_one(Static, id="zone_name").update(view.zone_name)
        self.query_one(Static, id="room_name").update(view.room_name)