from string import ascii_lowercase

from itertools import zip_longest

from core.ui.console.screens.base_screen import BaseConsoleScreen, pad
from core.ui.console.screens.item_detail import ItemDetailMixin
from core.ui.console import colors
from core.game.actions import Back, EquipItem, InspectEquipped, InspectItem, UnequipItem, UseItem
from core.items.base import Slot

# Lettre stable pour chaque slot d'équipement : a = main droite, b = main gauche...
SLOT_KEYS: dict[str, Slot] = dict(zip(ascii_lowercase, Slot))
KEY_OF_SLOT: dict[Slot, str] = {slot: key for key, slot in SLOT_KEYS.items()}


def clip(text: str, width: int) -> str:
    """Coupe un texte brut (sans couleurs) à `width` caractères."""
    return text if len(text) <= width else text[: max(0, width - 1)] + "."


class InventoryScreen(ItemDetailMixin, BaseConsoleScreen):
    BAR_WIDTH = 10
    BAR_WIDTH_COMPACT = 5
    COLUMN_MIN = 34        # en dessous, équipement et sac sont empilés
    SEPARATOR = " | "

    # ----- rendu -----

    def draw(self) -> None:
        if self.view.selected is None:
            self._draw_overview()
        else:
            self._draw_detail(self.view.selected)

    def _draw_overview(self) -> None:
        used = sum(1 for c in self.view.cases if c.item_id is not None)
        equipment_title = self.t("ui.inventory.equipment")
        bag_title = f"{self.t('ui.inventory.bag')} ({used}/{len(self.view.cases)})"
        inner = self.width - 4

        left_width = (inner - len(self.SEPARATOR)) // 2
        right_width = inner - len(self.SEPARATOR) - left_width
        if right_width >= self.COLUMN_MIN:
            left = [equipment_title, "", *self._equipment_lines(left_width)]
            right = [bag_title, "", *self._bag_lines(right_width)]
            lines = [pad(l, left_width) + self.SEPARATOR + r
                     for l, r in zip_longest(left, right, fillvalue="")]
            self.box(lines, header=self.t("ui.inventory.title"))
        else:
            lines = [*self._equipment_lines(inner), "", "", bag_title, "", *self._bag_lines(inner)]
            self.box(lines, header=self.t("ui.inventory.title"), title=equipment_title)
        print()
        print(self.color(self.t("ui.inventory.hint"), colors.LIGHT_GRAY))

    def _equipment_lines(self, width: int) -> list[str]:
        labels = {e.slot: self.t(f"ui.inventory.slots.{e.slot.value}") for e in self.view.equipment}
        label_width = max(len(label) for label in labels.values())
        lines = []
        for entry in self.view.equipment:
            prefix = f"  {KEY_OF_SLOT[entry.slot]}. {labels[entry.slot]:<{label_width}} : "
            if entry.item_id is None:
                lines.append(prefix + self.color(self.t("ui.inventory.empty"), colors.LIGHT_GRAY))
            else:
                lines.append(prefix + clip(self._item_name(entry.item_id), width - len(prefix)))
        return lines

    def _bag_lines(self, width: int) -> list[str]:
        occupied = [(i, c) for i, c in enumerate(self.view.cases) if c.item_id is not None]
        if not occupied:
            return [self.color(self.t("ui.inventory.empty_bag"), colors.LIGHT_GRAY)]
        labels = {i: self._item_name(c.item_id) + (f" x{c.quantity}" if c.quantity > 1 else "") for i, c in occupied}
        longest = max(len(label) for label in labels.values())
        room = width - 5                                   # place après le numéro de case
        # Barre réduite si la taille normale obligerait à couper les noms
        bar_width = self.BAR_WIDTH if room - longest >= self.BAR_WIDTH + 7 else self.BAR_WIDTH_COMPACT
        name_width = min(longest, room - bar_width - 7)
        lines = []
        for i, case in occupied:
            if case.wear is None:
                line = f"{i + 1:>3}. {clip(labels[i], width - 5)}"
            else:
                line = f"{i + 1:>3}. {clip(labels[i], name_width):<{name_width}}"
            if case.wear is not None:
                line += "  " + self._wear_bar(case.wear, bar_width)
            lines.append(line.rstrip())
        free = len(self.view.cases) - len(occupied)
        if free:
            lines.append("")
            lines.append(self.color(self.t("ui.inventory.free", count=free), colors.LIGHT_GRAY))
        return lines

    def _draw_detail(self, d) -> None:
        lines = self._detail_lines(d)
        self.box(lines, header=self.t("ui.inventory.title"), title=self._item_name(d.item_id))
        print()

    def _replaces(self, combo) -> str:
        """« (remplace X) » si des objets sont déjà portés sur ces slots."""
        worn = {e.slot: e.item_id for e in self.view.equipment if e.item_id is not None}
        names = list(dict.fromkeys(self._item_name(worn[s]) for s in combo if s in worn))
        return f" ({self.t('ui.inventory.replaces', item=', '.join(names))})" if names else ""

    def ask(self):
        if self.view.selected is not None:
            return self._ask_detail(self.view.selected)
        while True:
            try:
                raw = input("> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                return Back()
            if raw == "0":
                return Back()
            if raw.isdigit():
                index = int(raw) - 1
                if 0 <= index < len(self.view.cases) and self.view.cases[index].item_id is not None:
                    return InspectItem(index)
            elif raw in SLOT_KEYS:
                slot = SLOT_KEYS[raw]
                if any(e.slot is slot and e.item_id is not None for e in self.view.equipment):
                    return InspectEquipped(slot)
            print(self.t("ui.common.invalid_choice"))

    def _ask_detail(self, d):
        options = []

        if d.can_use:
            options.append((self.t("ui.inventory.use", item=self._item_name(d.item_id)), UseItem(d.index)))
        if d.can_equip:
            if len(d.slots) == 1:
                label = self.t("ui.inventory.equip", item=self._item_name(d.item_id))
                options.append((label + self._replaces(d.slots[0]), EquipItem(d.index, d.slots[0])))
            else:
                for combo in d.slots:
                    label = self.t("ui.inventory.equip_on", slot=self._slot_names(combo, " + "))
                    options.append((label + self._replaces(combo), EquipItem(d.index, combo)))
        if d.can_unequip:
            options.append((self.t("ui.inventory.unequip", item=self._item_name(d.item_id)), UnequipItem(d.equipped_on[0])))
        options.append((self.t("ui.common.back"), Back()))
        return self.choose(options)
