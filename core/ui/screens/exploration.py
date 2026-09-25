from core.ui.screens.base_screen import BaseScreen
from textual.widgets import Static, OptionList, Footer, Header, ProgressBar
from core.enums import Direction
from textual.binding import Binding
from core.enums import Stat
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Button, Footer, RichLog, Static
from textual.widgets.option_list import Option
from textual import on
from core.game.actions import NewGame, Quit, Move, Explore
from core.views.exploration_view import ExplorationView

class ExplorationScreen(BaseScreen):
    BINDINGS = [
        Binding("a",      "explore", "Explorer"),
        Binding("z/q/s/d", "", "Naviguer"),
        Binding("up,z",    "move('NORTH')", "Nord", show=False),
        Binding("down,s",  "move('SOUTH')", "Sud", show=False),
        Binding("left,q",  "move('WEST')",  "Ouest", show=False),
        Binding("right,d", "move('EAST')",  "Est", show=False),
        Binding("escape",  "quit_game",     "Quitter")]

    def compose(self):
        with Horizontal(id="main"):
            # Colonne de gauche : la salle, puis le journal
            with Vertical(id="left"):
                with Vertical(id="room-panel", classes="panel"):
                    yield Static("…", id="room-name")
                    yield Static("…", id="room-description")
                yield RichLog(id="log-panel", classes="panel")

            # Colonne de droite : la fiche, puis les directions
            with Vertical(id="right"):
                with Vertical(id="player-panel", classes="panel"):
                    yield Static("Lv.", id="player-level")
                    with Horizontal(id="hp-row"):
                        yield Static("PV", id="hp-label")
                        yield ProgressBar(id="hp-bar", show_percentage=False, show_eta=False)
                        yield Static("", id="hp-text")
                    yield Static("")
                    for stat in [s for s in Stat if s != Stat.HEALTH]:
                        yield Static(f"{stat.name.capitalize()}: 0", id=f"stat-{stat.name.lower()}") 
                with Grid(id="directions"):
                    yield Static("")
                    yield Button("N", id="move-NORTH", action="move('NORTH')")
                    yield Static("")
                    yield Button("O", id="move-WEST", action="move('WEST')")
                    yield Static("")
                    yield Button("E", id="move-EAST", action="move('EAST')")
                    yield Static("")
                    yield Button("S", id="move-SOUTH", action="move('SOUTH')")
                    yield Static("")
        yield Footer(id="footer")

    
    def update_view(self, view: ExplorationView):
        player = view.player_summary
        self.query_one("#room-panel").border_title = view.zone_name
        self.query_one("#room-name", Static).update(view.room_name)
        self.query_one("#room-description", Static).update(view.room_description)
        self.query_one("#player-panel").border_title = view.player_summary.name
        self.query_one("#player-level", Static).update(f"Lv. {view.player_summary.level}")
        self.query_one("#hp-bar", ProgressBar).update(total=player.max_health, progress=player.health)
        self.query_one("#hp-text", Static).update(f"{player.health}/{player.max_health}")
        for stat in [s for s in Stat if s != Stat.HEALTH]:
            self.query_one(f"#stat-{stat.name.lower()}", Static).update(f"{stat.name.capitalize()}: {player.stats.get(stat, 0)}")

    def on_mount(self) -> None:
        
        self.query_one("#log-panel").border_title = "JOURNAL"
        super().on_mount()   
    
    def action_move(self, direction: str) -> None:
        self.app.dispatch(Move(Direction[direction]))
    
    def action_quit_game(self) -> None:
        self.app.dispatch(Quit())
    
    def action_explore(self) -> None:
        self.app.dispatch(Explore())