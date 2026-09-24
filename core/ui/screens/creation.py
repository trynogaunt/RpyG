from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Input, Static

from core.enums import Stat
from core.game.actions import AllocatePoints, ConfirmCreation, SetName
from core.game.rules import STAT_RULES
from core.ui.screens.base_screen import BaseScreen
from core.views.creation_view import CreationView


class CreationScreen(BaseScreen):
    DEFAULT_CSS = """
    CreationScreen .stat-row { height: auto; }
    CreationScreen .stat-label { width: 12; height: 3; content-align: left middle; }
    CreationScreen .stat-value { width: 6; height: 3; content-align: center middle; }
    """

    def compose(self) -> ComposeResult:
        yield Static("Création du personnage")
        yield Input(placeholder="Nom du personnage", id="name")
        for stat in STAT_RULES:
            with Horizontal(classes="stat-row"):
                yield Static(stat.name.capitalize(), classes="stat-label")
                yield Button("-", id=f"remove-{stat.name}")
                yield Static("", id=f"value-{stat.name}", classes="stat-value")
                yield Button("+", id=f"add-{stat.name}")
        yield Static("", id="points-left")
        yield Button("Confirmer", id="confirm", variant="primary")

    def update_view(self, view: CreationView) -> None:
        for stat, value in view.stats_values.items():
            self.query_one(f"#value-{stat.name}", Static).update(str(value))
            self.query_one(f"#add-{stat.name}", Button).disabled = not view.can_add[stat]
            self.query_one(f"#remove-{stat.name}", Button).disabled = not view.can_remove[stat]
        self.query_one("#points-left", Static).update(f"Points restants : {view.points_left}")
        self.query_one("#confirm", Button).disabled = not view.can_confirm

    @on(Input.Changed, "#name")
    def name_changed(self, event: Input.Changed) -> None:
        self.app.dispatch(SetName(event.value))

    @on(Button.Pressed)
    def button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.app.dispatch(ConfirmCreation())
            return
        kind, stat_name = event.button.id.split("-", 1)
        delta = +1 if kind == "add" else -1
        self.app.dispatch(AllocatePoints(Stat[stat_name], delta))