from textual import on
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.widgets import Button, Footer, ProgressBar, RichLog, Static

from core.game.actions import AttackEnemy, Flee, Quit
from core.game.response import Message
from core.ui.textual.screens.base_screen import BaseScreen
from core.views.combat_view import CombatView


class Fighter(Vertical):
    """Panneau d'un combattant : barre de PV et valeur."""

    def compose(self):
        with Horizontal(classes="fighter-hp"):
            yield ProgressBar(show_percentage=False, show_eta=False)
            yield Static("", classes="fighter-hp-text")

    def set_health(self, name: str, health: int, max_health: int) -> None:
        self.border_title = name
        self.query_one(ProgressBar).update(total=max_health, progress=health)
        self.query_one(".fighter-hp-text", Static).update(f"{health}/{max_health}")


class CombatScreen(BaseScreen):
    """Joueur à gauche, ennemis empilés à droite, journal des coups en dessous."""

    BINDINGS = [
        Binding("a,enter", "attack", "ui.combat.attack"),
        Binding("f,escape", "flee", "ui.combat.flee"),
    ]

    def __init__(self, view: CombatView | None = None, **kwargs):
        super().__init__(view=view, **kwargs)
        self.view = view
        self._logged = 0                      # entrées du journal déjà écrites

    def compose(self):
        with Horizontal(id="combat-fighters"):
            yield Fighter(id="combat-player", classes="panel")
            # Les ennemis ne changent pas pendant un combat : un panneau chacun, morts compris
            with Vertical(id="combat-enemies"):
                for i in range(len(self.view.foes) if self.view else 0):
                    yield Fighter(id=f"combat-enemy-{i}", classes="panel enemy")
        yield RichLog(id="combat-log", classes="panel", wrap=True, markup=True, min_width=0)
        with Horizontal(id="combat-actions"):
            yield Button(id="combat-attack", variant="error")
            yield Button(id="combat-flee")
        yield Footer()

    def on_mount(self) -> None:
        t = self.app.t
        self.query_one("#combat-log").border_title = t("ui.combat.log")
        self.query_one("#combat-attack", Button).label = t("ui.combat.attack")
        self.query_one("#combat-flee", Button).label = t("ui.combat.flee")
        super().on_mount()

    def update_view(self, view: CombatView) -> None:
        self.view = view
        p = view.player_summary
        self.query_one("#combat-player", Fighter).set_health(p.name, p.health, p.max_health)
        for i, foe in enumerate(view.foes):
            self.query_one(f"#combat-enemy-{i}", Fighter).set_health(self._foe_name(i), foe.health, foe.max_health)

        log = self.query_one("#combat-log", RichLog)
        for entry in view.log[self._logged:]:
            enemy = self._foe_name(entry.foe)
            if entry.blocked:
                key = "ui.combat.player_blocked" if entry.attacker == "player" else "ui.combat.enemy_blocked"
                log.write(f"[cyan]#[/] [italic]{self.app.t(key, enemy=enemy)}[/]")
                continue
            if entry.attacker == "player":
                line = f"[#ffb000]>[/] {self.app.t('ui.combat.player_hits', enemy=enemy, damage=entry.damage)}"
            else:
                line = f"[red]<[/] {self.app.t('ui.combat.enemy_hits', enemy=enemy, damage=entry.damage)}"
            if entry.crit:
                line += f" [bold #ffb000]{self.app.t('ui.combat.critical')}[/]"
            log.write(line)
        self._logged = len(view.log)

    def _foe_name(self, index: int) -> str:
        foe = self.view.foes[index]
        name = self.app.t(f"enemies.{foe.enemy_id}.name")
        return f"{name} {foe.tag}" if foe.tag else name

    def action_attack(self) -> None:
        self.app.dispatch(AttackEnemy())

    def action_flee(self) -> None:
        self.app.dispatch(Flee())

    @on(Button.Pressed, "#combat-attack")
    def _on_attack(self) -> None:
        self.action_attack()

    @on(Button.Pressed, "#combat-flee")
    def _on_flee(self) -> None:
        self.action_flee()


class GameOverScreen(BaseScreen):
    BINDINGS = [
        Binding("enter,escape", "back", "ui.exploration.back_to_menu"),
    ]

    def compose(self):
        with Vertical(id="game-over"):
            yield Static(id="game-over-title")
            yield Static(id="game-over-message")
            with Center():
                yield Button(id="game-over-back", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        t = self.app.t
        self.query_one("#game-over-title", Static).update(t("ui.combat.game_over"))
        self.query_one("#game-over-back", Button).label = t("ui.exploration.back_to_menu")
        super().on_mount()

    def show_messages(self, messages: tuple[Message, ...]) -> None:
        text = "\n".join(self.app.resolve_message(self.app.translation, m) for m in messages)
        self.query_one("#game-over-message", Static).update(text)

    def action_back(self) -> None:
        self.app.dispatch(Quit())

    @on(Button.Pressed, "#game-over-back")
    def _on_back(self) -> None:
        self.action_back()
