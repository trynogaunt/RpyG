from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.ui.console import colors
from core.game.actions import Move, Explore, Quit, SaveGame, OpenSlots, OpenInventory, StartCombat


class ExplorationScreen(BaseConsoleScreen):
    def draw(self):
        v = self.view
        p = v.player_summary
        name = self.app.t(f'zones.{v.zone_id}.rooms.{v.room_id}.name')
        room_description = self.app.t(f'zones.{v.zone_id}.rooms.{v.room_id}.description') if v.room_id else v.description
        lines = [room_description]
        if v.encounters:
            names = " / ".join(self._encounter_label(e) for e in v.encounters)
            lines += ["", self.color(self.t("ui.exploration.enemies", names=names), colors.RED)]
        self.box(lines, header=self.t(f"zones.{v.zone_id}.name"), title=name)
        print()
        self.draw_player(p)
        print()

    def _encounter_label(self, encounter) -> str:
        """« Rat des Cavernes x2, Chauve-souris des Cavernes »."""
        return ", ".join(self.t(f"enemies.{enemy_id}.name") + (f" x{count}" if count > 1 else "")
                         for enemy_id, count in encounter.enemies)

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
        for encounter in v.encounters:
            label = self.t("ui.combat.fight", enemy=self._encounter_label(encounter))
            options.append((label, StartCombat(encounter.id)))
        options.append((self.t("ui.exploration.look_around"), Explore()))
        options.append((self.t("ui.exploration.open_inventory"), OpenInventory()))
        options.append((self.t("ui.exploration.save_game"), OpenSlots(mode="save")))
        options.append((self.t("ui.exploration.back_to_menu"), Quit()))
        return self.choose(options)