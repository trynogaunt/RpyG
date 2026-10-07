from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Label, RadioButton, RadioSet

from core.game.actions import Back, SetLocale


class OptionsScreen(Screen):
    BINDINGS = [Binding("escape", "back", "Retour")]

    DEFAULT_CSS = """
    OptionsScreen { align: center middle; background: #111111; }
    #options-box { width: 60; height: auto; padding: 1 2; border: round #ffb000; }
    #options-title { width: 100%; content-align: center middle;
                     text-style: bold; color: #ffb000; margin-bottom: 1; }
    .section { color: #c5cdd9; margin-top: 1; }
    #locale-set { width: 100%; border: none; background: transparent; }
    #back { margin-top: 1; width: 100%; }
    """

    def __init__(self, view):
        super().__init__()
        self._view = view

    # ----- rendu -----

    def compose(self) -> ComposeResult:
        t = self.app.t
        with Vertical(id="options-box"):
            yield Label(t("ui.options.title"), id="options-title")
            yield Label(t("ui.options.language"), classes="section")
            with RadioSet(id="locale-set"):
                for code in self._view.available_locales:
                    yield RadioButton(
                        t(f"ui.options.language_name.{code}"),
                        value=(code == self._view.locale),
                        name=code,
                    )
            yield Button(t("ui.common.back"), id="back")

    # ----- contrat avec TextualApp.show() -----

    def update_view(self, view) -> None:
        """Appelé quand la réponse reste sur cet écran (ex. changement de langue)."""
        self._view = view
        self.refresh(recompose=True)      # reconstruit les widgets avec les nouveaux textes

    def show_messages(self, messages) -> None:
        pass                              # cet écran n'affiche pas de messages

    # ----- entrées -----

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        code = event.pressed.name
        # Textual émet aussi cet événement au montage : on ignore la langue déjà active.
        if code and code != self._view.locale:
            self.app.dispatch(SetLocale(code))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.dispatch(Back())

    def action_back(self) -> None:
        self.app.dispatch(Back())