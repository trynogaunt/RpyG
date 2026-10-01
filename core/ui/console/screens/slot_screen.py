from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import LoadGame, SaveGame, Back
from datetime import datetime


class SlotScreen(BaseConsoleScreen):
    def draw(self):
        self.rule()
        self.centered(self.t(f"ui.slots.title_{self.view.mode}"))
        self.rule()
        print()

    def ask(self):
        v = self.view
        make_action = LoadGame if v.mode == "load" else SaveGame
        options = []
        for s in sorted(v.slots, key=lambda x: x.slot):
            if not s.readable:
                label, action = f"{self.t('ui.slots.unreadable')}", None
            elif s.name is None:
                label = f"{self.t('ui.slots.empty')}"
                action = make_action(s.slot) if v.mode == "save" else None
            else:
                label = f"{s.name}, {self.t('ui.common.level')} {s.level}, {s.location}"
                action = make_action(s.slot)
            options.append((label, action))
        options.append((self.t("ui.common.back"), Back()))
        return self.choose(options)