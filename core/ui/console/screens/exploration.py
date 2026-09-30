from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.ui.console import colors
from core.game.actions import Move, Explore, Quit


class ExplorationScreen(BaseConsoleScreen):
    def draw(self):
        v = self.view
        p = v.player_summary
        name = self.app.t(f'zones.{v.zone_id}.rooms.{v.room_id}.name')
        room_description = self.app.t(f'zones.{v.zone_id}.rooms.{v.room_id}.description') if v.room_id else v.description
        self.box([room_description], header=self.t(f"zones.{v.zone_id}.name"), title=name)
        print()
        self.draw_player(p)
        print()

    def draw_player(self, p):
        bar_len = 20
        filled = round(bar_len * p.health / p.max_health) if p.max_health else 0
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"{p.name}  {self.t('ui.common.level')} {p.level}")
        print(f"{self.t('ui.stats.health')} {self.color(bar, colors.GREEN)} {p.health}/{p.max_health}")
        print("  ".join(
            f"{self.t(f'ui.stats.{stat.name.lower()}')} {value}"
            for stat, value in p.stats.items()
        ))

    def ask(self):
        v = self.view
        options = []
        for direction, allowed in v.can_move.items():
            if allowed:
                label = self.t(f"ui.directions.{direction.name.lower()}")
                options.append((label, Move(direction=direction)))
        options.append((self.t("ui.exploration.look_around"), Explore()))
        options.append((self.t("ui.exploration.back_to_menu"), Quit()))
        return self.choose(options)