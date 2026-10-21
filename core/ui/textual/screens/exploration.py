from core.ui.textual.screens.base_screen import BaseScreen
from textual.widgets import Static, OptionList, Footer, Header, ProgressBar
from core.enums import Direction
from textual.binding import Binding
from core.enums import Stat
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Button, Footer, RichLog, Static
from textual.widgets.option_list import Option
from textual import on
from core.game.actions import NewGame, Quit, Move, Explore, OpenSlots, OpenInventory, StartCombat
from core.game.response import Message
from core.views.exploration_view import ExplorationView
from core.game.text_keys import room_key, zone_key

class ExplorationScreen(BaseScreen):
    BINDINGS = [
        Binding("a",      "explore", "ui.exploration.look_around"),
        Binding("z/q/s/d", "", "ui.exploration.navigation"),
        Binding("up,z",    "move('NORTH')", "", show=False),
        Binding("down,s",  "move('SOUTH')", "", show=False),
        Binding("left,q",  "move('WEST')",  "", show=False),
        Binding("right,d", "move('EAST')",  "", show=False),
        Binding("c", "fight", "ui.combat.fight_short"),
        Binding("i", "open_inventory", "ui.exploration.open_inventory"),
        Binding("e", "save_game", "ui.exploration.save_game"),
        Binding("escape",  "quit_game", "ui.common.quit")]

    def compose(self):
        with Horizontal(id="main"):
            # Colonne de gauche : la salle, puis le journal
            with Vertical(id="left"):
                with Vertical(id="room-panel", classes="panel"):
                    yield Static("…", id="room-name")
                    yield Static("…", id="room-description")
                    yield Static("", id="room-enemies")
                yield RichLog(id="log-panel", classes="panel", wrap=True, highlight=True, min_width=0)

            with Vertical(id="right"):
                with Vertical(id="player-panel", classes="panel"):
                    yield Static("Lv.", id="player-level")
                    with Horizontal(id="hp-row"):
                        yield Static("HP", id="hp-label")
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
        self.view = view
        player = view.player_summary
        self.query_one("#room-panel").border_title = self.app.t(zone_key(view.zone_id, "name"))
        self.query_one("#room-name", Static).update(self.app.t(f'zones.{view.zone_id}.rooms.{view.room_id}.name'))
        self.query_one("#room-description", Static).update(self.app.t(f'zones.{view.zone_id}.rooms.{view.room_id}.description'))
        enemies = self.query_one("#room-enemies", Static)
        enemies.display = bool(view.encounters)
        self.refresh_bindings()          # « Combattre » n'apparaît que face à un ennemi
        if view.encounters:
            names = " / ".join(self._encounter_label(e) for e in view.encounters)
            enemies.update(self.app.t("ui.exploration.enemies", names=names))
        self.query_one("#player-panel").border_title = view.player_summary.name
        xp = f"{player.xp}/{player.xp_next}" if player.xp_next is not None else f"{player.xp}"
        self.query_one("#player-level", Static).update(f"Lv. {player.level}  {self.app.t('ui.stats.xp')} {xp}")
        self.query_one("#hp-label", Static).update(self.app.t("ui.stats.abrev.health"))
        self.query_one("#hp-bar", ProgressBar).update(total=player.max_health, progress=player.health)
        self.query_one("#hp-text", Static).update(f"{player.health}/{player.max_health}")
        for stat in [s for s in Stat if s != Stat.HEALTH]:
            self.query_one(f"#stat-{stat.name.lower()}", Static).update(f"{self.app.t(f'ui.stats.{stat.name.lower()}')}: {player.stats.get(stat, 0)}")

    def show_messages(self, messages: tuple[Message, ...]) -> None:
        log_panel = self.query_one("#log-panel", RichLog)
        for message in messages:
            key = message.key
            if message.fallback_key and not self.app.translation.has(key):
                key = message.fallback_key
            log_panel.write(f"> {self.app.t(key, **message.params)}")

    def on_mount(self) -> None:
        
        self.query_one("#log-panel").border_title = "JOURNAL"
        super().on_mount()   
    
    def check_action(self, action: str, parameters) -> bool | None:
        if action == "fight":
            view = getattr(self, "view", None)
            return bool(view and view.encounters)
        return True

    def action_fight(self) -> None:
        """Affronte le premier groupe de la salle."""
        if self.view.encounters:
            self.app.dispatch(StartCombat(self.view.encounters[0].id))

    def _encounter_label(self, encounter) -> str:
        """« Rat des Cavernes x2, Chauve-souris des Cavernes »."""
        return ", ".join(self.app.t(f"enemies.{enemy_id}.name") + (f" x{count}" if count > 1 else "")
                         for enemy_id, count in encounter.enemies)

    def action_open_inventory(self) -> None:
        self.app.dispatch(OpenInventory())

    def action_save_game(self) -> None:
        self.app.dispatch(OpenSlots(mode="save"))

    def action_move(self, direction: str) -> None:
        self.app.dispatch(Move(Direction[direction]))
    
    def action_quit_game(self) -> None:
        self.app.dispatch(Quit())
    
    def action_explore(self) -> None:
        self.app.dispatch(Explore())