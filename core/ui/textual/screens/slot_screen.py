from datetime import datetime

from textual.binding import Binding
from textual.widgets import Footer, OptionList, Static
from textual.widgets.option_list import Option
from textual.containers import Center, Vertical

from core.game.actions import Back, LoadGame, SaveGame
from core.ui.textual.screens.base_screen import BaseScreen

BINDINGS = [Binding("escape", "back", "Back")]

class SlotsScreen(BaseScreen):
    def __init__(self, view=None, **kwargs):
        super().__init__(**kwargs)
        self.view = view

    def update_view(self, view):
        self.view = view
        if self.is_mounted:
            self._refresh()

    def compose(self):
        with Center():
            with Vertical(id="slots-box"):
                yield Static(id="slots-title")
                yield OptionList(id="slots-list")
                yield Static(id="slots-message")
        yield Footer()

    def on_mount(self):
        self._refresh()

    def _selectable(self, s) -> bool:
        return s.readable and (self.view.mode == "save" or s.name is not None)

    def _label(self, s) -> str:
        t = self.app.t
        if not s.readable:
            return f"{s.slot}. {t('ui.slots.unreadable')}"
        if s.name is None:
            return f"{s.slot}. {t('ui.slots.empty')}"
        return f"{s.slot}. {s.name} - {t('ui.common.level')} {s.level} - {s.location}"

    def _refresh(self):
        self.query_one("#slots-title", Static).update(
            self.app.t(f"ui.slots.title_{self.view.mode}")
        )
        lst = self.query_one("#slots-list", OptionList)
        lst.clear_options()
        for s in self.view.slots:
            lst.add_option(Option(self._label(s), id=f"slot-{s.slot}",
                                  disabled=not self._selectable(s)))
        self.query_one("#slots-message", Static).update("")

    def on_option_list_option_selected(self, event):
        slot = int(event.option_id.removeprefix("slot-"))
        action = LoadGame(slot) if self.view.mode == "load" else SaveGame(slot)
        self.app.dispatch(action)

    def action_back(self):
        self.app.dispatch(Back())

    def show_messages(self, messages):
        text = " ".join(self.app.resolve_message(self.app.translation, m) for m in messages)
        self.query_one("#slots-message", Static).update(text)