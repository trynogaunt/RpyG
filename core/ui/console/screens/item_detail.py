from core.ui.console import colors


class ItemDetailMixin:
    """Fiche d'objet (ItemDetailView) partagée par les écrans inventaire et catalogue."""

    BAR_WIDTH = 10

    def _detail_lines(self, d) -> list[str]:
        rows: list[tuple[str, str]] = []
        if d.category:
            rows.append((self.t("ui.inventory.details.category"), self.t(f"ui.inventory.categories.{d.category}")))
        if d.equipped_on:
            rows.append((self.t("ui.inventory.details.equipped_on"), self._slot_names(d.equipped_on, " + ")))
        elif d.slots:
            sep = f" {self.t('ui.inventory.details.or')} "
            rows.append((self.t("ui.inventory.details.slots"), sep.join(self._slot_names(c, " + ") for c in d.slots)))
        if d.quantity > 1:
            rows.append((self.t("ui.inventory.details.quantity"), f"x{d.quantity}"))
        if d.wear is not None:
            rows.append((self.t("ui.inventory.details.wear"), self._wear_bar(d.wear)))
        if d.attack:
            rows.append((self.t("ui.inventory.details.attack"), ", ".join([
                f"{self.t('ui.inventory.details.damage')} x{d.attack.damage_multiplier:g}",
                f"{self.t('ui.inventory.details.crit')} x{d.attack.crit_multiplier:g}",
                f"{self.t('ui.inventory.details.hits')} {d.attack.hits}",
            ])))
        if d.defense:
            rows.append((self.t("ui.inventory.details.defense"), ", ".join([
                f"{self.t('ui.inventory.details.armor')} x{d.defense.armor_multiplier:g}",
                f"{self.t('ui.inventory.details.magic_resistance')} x{d.defense.magic_resistance:g}",
                f"{self.t('ui.inventory.details.block_chance')} {d.defense.block_chance:.0%}",
            ])))

        lines = [self.t(f"items.{d.item_id}.description")]
        if rows:
            lines.append("")
            label_width = max(len(label) for label, _ in rows)
            lines += [f"{label:<{label_width}} : {value}" for label, value in rows]
        return lines

    def _slot_names(self, slots, sep: str) -> str:
        return sep.join(self.t(f"ui.inventory.slots.{s.value}") for s in slots)

    def _wear_bar(self, wear: float, bar_width: int = BAR_WIDTH) -> str:
        filled = round(bar_width * wear)
        code = colors.GREEN if wear > 0.6 else colors.YELLOW if wear > 0.3 else colors.RED
        bar = self.color("█" * filled + "░" * (bar_width - filled), code)
        return f"{bar} {round(wear * 100):>3}%"
