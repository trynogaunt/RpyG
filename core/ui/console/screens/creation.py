from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import AllocatePoints, ConfirmCreation, SetName

class CreationScreen(BaseConsoleScreen):
    def draw(self):
        v = self.view
        self.rule()
        self.centered(self.t("ui.creation.title"))
        self.rule()
        print(f"{self.t('ui.creation.name')} : {v.name or '-'}")
        print(f"{self.t('ui.creation.points_left')} : {v.points_left}")
        print()
        for stat, value in v.stats_values.items():
            print(f"  {self.t(f'ui.stats.{stat.name.lower()}')} : {value}")
        print()

    def ask(self):
        v = self.view
        options = [(self.t("ui.creation.set_name"), self.ask_name)]
        for stat in v.stats_values:
            label = self.t(f"ui.stats.{stat.name.lower()}")
            if v.can_add[stat]:
                options.append((f"{label} +", AllocatePoints(stat, 1)))
            if v.can_remove[stat]:
                options.append((f"{label} -", AllocatePoints(stat, -1)))
        if v.can_confirm:
            options.append((self.t("ui.creation.confirm"), ConfirmCreation()))
        return self.choose(options)