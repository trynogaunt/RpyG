import re
import shutil
from itertools import zip_longest

from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import EquipItem, UnequipItem, Back

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def visible_len(s: str) -> int:
    return len(ANSI.sub("", s))


def pad(s: str, width: int) -> str:
    return s + " " * max(0, width - visible_len(s))


class InventoryScreen(BaseConsoleScreen):
    LEFT_WIDTH = 30
    RIGHT_WIDTH = 34
    GAP = 2

    def draw(self) -> None:
        self.rule()
        self.centered(self.t("ui.inventory.title"))
        self.rule()
        print()

        equipment = self._block(
            self.t("ui.inventory.equipment"), self._equipment_lines(), self.LEFT_WIDTH
        )
        bag = self._block(
            self.t("ui.inventory.bag"), self._bag_lines(), self.RIGHT_WIDTH
        )

        needed = self.LEFT_WIDTH + self.GAP + self.RIGHT_WIDTH
        if shutil.get_terminal_size().columns >= needed:
            for left, right in zip_longest(equipment, bag, fillvalue=""):
                print(pad(left, self.LEFT_WIDTH) + " " * self.GAP + right)
        else:
            print("\n".join(equipment))
            print()
            print("\n".join(bag))
        print()

    def ask(self):
        options = []
        for i, case in enumerate(self.view.cases):
            if case.equippable:
                label = self.t("ui.inventory.equip", item=self._item_label(case))
                options.append((label, EquipItem(index=i)))
        for entry in self.view.equipment:
            if entry.item_id is not None:
                label = self.t("ui.inventory.unequip", item=self._item_name(entry.item_id))
                options.append((label, UnequipItem(slot=entry.slot)))
        options.append((self.t("ui.common.back"), Back()))
        return self.choose(options)

    def _item_name(self, item_id: str) -> str:
        return self.t(f"items.{item_id}.name")

    def _item_label(self, case) -> str:
        name = self._item_name(case.item_id)
        if case.wear is not None:
            name = f"{name} ({round(case.wear * 100)}%)"
        return f"{name} x{case.quantity}" if case.quantity > 1 else name

    def _bag_lines(self) -> list[str]:
        lines = []
        for i, slot in enumerate(self.view.cases):
            if slot.item_id is None:
                content = self.t("ui.inventory.empty")
            else:
                content = self._item_label(slot)
            lines.append(f"{i + 1:>2}. {content}")
        return lines

    def _equipment_lines(self) -> list[str]:
        lines = []
        for entry in self.view.equipment:
            label = self.t(f"ui.inventory.slots.{entry.slot.value}")
            value = (
                self.t("ui.inventory.empty")
                if entry.item_id is None
                else self._item_name(entry.item_id)
            )
            lines.append(f"{label}: {value}")
        return lines

    # --- cadre et mise en page ---

    def _block(self, title: str, lines: list[str], width: int) -> list[str]:
        prefix = f"┌─ {title} "
        top = prefix + "─" * max(0, width - visible_len(prefix) - 1) + "┐"
        body = [f"│ {pad(line, width - 4)} │" for line in lines]
        bottom = "└" + "─" * (width - 2) + "┘"
        return [top, *body, bottom]