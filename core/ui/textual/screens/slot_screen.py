from datetime import datetime

from textual.binding import Binding
from textual.widgets import Footer, OptionList, Static
from textual.widgets.option_list import Option
from textual.containers import Center, Vertical

from core.game.actions import Back, ConfirmDelete, DeleteSave, LoadGame, SaveGame, SelectSlot
from core.ui.console.screens.slot_screen import format_date
from core.ui.textual.screens.base_screen import BaseScreen

class SlotsScreen(BaseScreen):
    BINDINGS = [Binding("escape", "back", "ui.common.back")]

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
        if self.view.mode == "save":
            return s.readable
        return not s.readable or s.name is not None

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
        t = self.app.t
        s = self.view.selected
        if s is None:
            for slot in self.view.slots:
                lst.add_option(Option(self._label(slot), id=f"slot-{slot.slot}",
                                      disabled=not self._selectable(slot)))
            self.query_one("#slots-message", Static).update("")
        elif self.view.confirm_delete:
            self.query_one("#slots-message", Static).update(
                t("ui.slots.confirm_delete", name=s.name or f"#{s.slot}")
            )
            lst.add_option(Option(t("ui.slots.yes"), id="confirm-delete"))
            lst.add_option(Option(t("ui.slots.no"), id="back"))
        else:
            details = self._label(s)
            if s.readable:
                details += "\n" + t("ui.slots.saved_at", date=format_date(s.saved_at))
            self.query_one("#slots-message", Static).update(details)
            lst.add_option(Option(t("ui.slots.load"), id="load", disabled=not s.readable))
            lst.add_option(Option(t("ui.slots.delete"), id="delete"))
            lst.add_option(Option(t("ui.common.back"), id="back"))
        lst.highlighted = next((i for i in range(lst.option_count) if not lst.get_option_at_index(i).disabled), None)

    def on_option_list_option_selected(self, event):
        option_id = event.option_id
        selected = self.view.selected
        if option_id.startswith("slot-"):
            slot = int(option_id.removeprefix("slot-"))
            action = SelectSlot(slot) if self.view.mode == "load" else SaveGame(slot)
        elif option_id == "load":
            action = LoadGame(selected.slot)
        elif option_id == "delete":
            action = DeleteSave(selected.slot)
        elif option_id == "confirm-delete":
            action = ConfirmDelete()
        else:
            action = Back()
        self.app.dispatch(action)

    def action_back(self):
        self.app.dispatch(Back())

    def show_messages(self, messages):
        if not messages:
            return                        # garde le détail ou la question affichés par _refresh
        text =" ".join(self.app.resolve_message(self.app.translation, m) for m in messages)
        self.query_one("#slots-message", Static).update(text)