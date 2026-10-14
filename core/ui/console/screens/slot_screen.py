from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import LoadGame, SaveGame, SelectSlot, DeleteSave, ConfirmDelete, Back
from datetime import datetime


def format_date(saved_at: str | None) -> str:
    try:
        return datetime.fromisoformat(saved_at).strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return saved_at or "-"


class SlotScreen(BaseConsoleScreen):
    def draw(self):
        self.rule()
        self.centered(self.t(f"ui.slots.title_{self.view.mode}"))
        self.rule()
        print()
        s = self.view.selected
        if s is not None:
            if s.readable:
                print(self._summary(s))
                print(self.t("ui.slots.saved_at", date=format_date(s.saved_at)))
            else:
                print(f"{s.slot}. {self.t('ui.slots.unreadable')}")
            print()

    def _summary(self, s) -> str:
        return f"{s.name}, {self.t('ui.common.level')} {s.level}, {s.location}"

    def ask(self):
        v = self.view
        if v.selected is None:
            return self.choose(self._list_options())
        s = v.selected
        if v.confirm_delete:
            print(self.t("ui.slots.confirm_delete", name=s.name or f"#{s.slot}"))
            return self.choose([(self.t("ui.slots.yes"), ConfirmDelete()), (self.t("ui.slots.no"), Back())])
        return self.choose([
            (self.t("ui.slots.load"), LoadGame(s.slot) if s.readable else None),
            (self.t("ui.slots.delete"), DeleteSave(s.slot)),
            (self.t("ui.common.back"), Back()),
        ])

    def _list_options(self):
        v = self.view
        options = []
        for s in sorted(v.slots, key=lambda x: x.slot):
            if v.mode == "save":
                if not s.readable:
                    label, action = self.t("ui.slots.unreadable"), None
                elif s.name is None:
                    label, action = self.t("ui.slots.empty"), SaveGame(s.slot)
                else:
                    label, action = self._summary(s), SaveGame(s.slot)
            elif not s.readable:
                label, action = self.t("ui.slots.unreadable"), SelectSlot(s.slot)
            elif s.name is None:
                label, action = self.t("ui.slots.empty"), None
            else:
                label, action = self._summary(s), SelectSlot(s.slot)
            options.append((label, action))
        options.append((self.t("ui.common.back"), Back()))
        return options
