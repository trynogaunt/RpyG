from core.game.actions import AttackEnemy, Flee, Quit
from core.ui.console import colors
from core.ui.console.screens.base_screen import BaseConsoleScreen

BAR_WIDTH = 20
LOG_LINES = 4


class CombatScreen(BaseConsoleScreen):
    def draw(self):
        v = self.view
        p = v.player_summary
        enemy = self._enemy_name()
        label_width = max(len(p.name), len(enemy))

        lines = [
            "",
            f"{enemy:<{label_width}}  {self._bar(v.enemy_health, v.enemy_max_health, colors.RED)}",
            f"{p.name:<{label_width}}  {self._bar(p.health, p.max_health, colors.GREEN)}",
            "",
        ]
        for entry in v.log[-LOG_LINES:]:
            key = "ui.combat.player_hits" if entry.attacker == "player" else "ui.combat.enemy_hits"
            text = f"> {self.t(key, enemy=enemy, damage=entry.damage)}"
            if entry.crit:
                text += f" {self.t('ui.combat.critical')}"
            lines.append(self.color(text, colors.YELLOW if entry.crit else colors.LIGHT_GRAY))
        self.box(lines, header=self.t("ui.combat.title"))
        print()

    def _bar(self, health: int, max_health: int, code: str) -> str:
        filled = round(BAR_WIDTH * health / max_health) if max_health else 0
        bar = "█" * filled + "░" * (BAR_WIDTH - filled)
        return f"{self.color(bar, code)} {health}/{max_health}"

    def _enemy_name(self) -> str:
        return self.t(f"enemies.{self.view.enemy_id}.name")

    def ask(self):
        return self.choose([
            (self.t("ui.combat.attack"), AttackEnemy()),
            (self.t("ui.combat.flee"), Flee()),
        ])


class GameOverScreen(BaseConsoleScreen):
    def draw(self):
        print("\n" * 2)
        self.rule()
        self.centered(self.t("ui.combat.game_over"), colors.RED)
        self.rule()
        print()

    def ask(self):
        return self.choose([(self.t("ui.exploration.back_to_menu"), Quit())])
