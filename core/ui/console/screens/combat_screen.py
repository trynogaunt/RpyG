from core.game.actions import AttackEnemy, Flee, Quit
from core.ui.console import colors
from core.ui.console.screens.base_screen import BaseConsoleScreen, fit

BAR_WIDTH = 10
LOG_LINES = 4


class CombatScreen(BaseConsoleScreen):
    def draw(self):
        """Joueur à gauche, ennemis à droite, journal sur toute la largeur en dessous."""
        v = self.view
        p = v.player_summary
        names = [self._foe_name(i) for i in range(len(v.foes))]

        xp = f"{p.xp}/{p.xp_next}" if p.xp_next is not None else f"{p.xp}"
        player = [
            f"{p.name}  {self.t('ui.common.level')} {p.level}",
            self._bar(p.health, p.max_health, colors.GREEN),
            f"{self.t('ui.stats.xp')} {xp}",
            "  ".join(f"{self.t(f'ui.stats.abrev.{stat.name.lower()}')} {value}" for stat, value in p.stats.items()),
        ]
        foes = []
        right_width = (self.column_widths() or (0, self.width - 4))[1]
        for name, foe in zip(names, v.foes):
            # Un ennemi à terre reste affiché, grisé, pour garder les lettres A, B... à leur place
            name = fit(name, right_width)                 # avant la couleur : fit() ne coupe pas un texte coloré
            foes.append(name if foe.health > 0 else self.color(name, colors.LIGHT_GRAY))
            foes.append(self._bar(foe.health, foe.max_health, colors.RED))

        lines = self.columns([""] + player, [""] + foes) + [self.column_rule()]
        for entry in v.log[-LOG_LINES:]:
            enemy = names[entry.foe]
            if entry.blocked:
                key = "ui.combat.player_blocked" if entry.attacker == "player" else "ui.combat.enemy_blocked"
                lines.append(self.color(f"> {self.t(key, enemy=enemy)}", colors.CYAN))
                continue
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

    def _foe_name(self, index: int) -> str:
        foe = self.view.foes[index]
        name = self.t(f"enemies.{foe.enemy_id}.name")
        return f"{name} {foe.tag}" if foe.tag else name

    def ask(self):
        living = [i for i, foe in enumerate(self.view.foes) if foe.health > 0]
        if len(living) == 1:
            attacks = [(self.t("ui.combat.attack"), AttackEnemy(living[0]))]
        else:                                   # une ligne par cible vivante
            attacks = [(self.t("ui.combat.attack_target", enemy=self._foe_name(i)), AttackEnemy(i)) for i in living]
        return self.choose([*attacks, (self.t("ui.combat.flee"), Flee())])


class GameOverScreen(BaseConsoleScreen):
    def draw(self):
        print("\n" * 2)
        self.rule()
        self.centered(self.t("ui.combat.game_over"), colors.RED)
        self.rule()
        print()

    def ask(self):
        return self.choose([(self.t("ui.exploration.back_to_menu"), Quit())])
