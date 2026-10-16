from itertools import groupby

from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.ui.console.screens.item_detail import ItemDetailMixin
from core.game.actions import CloseCatalog, InspectCatalogItem
from core.ui.console import colors
from core.ui.text_sort import sort_key


class CatalogScreen(ItemDetailMixin, BaseConsoleScreen):
    def sorted_entries(self):
        """Entrées groupées par catégorie, puis triées par nom traduit."""
        return sorted(
            self.view.entries,
            key=lambda e: (e.category or "", sort_key(self._item_name(e.item_id))),
        )

    def draw(self):
        entries = self.sorted_entries()
        selected_id = self.view.selected.item_id if self.view.selected else None
        lines = [""]
        number = 1
        for category, group in groupby(entries, key=lambda e: e.category):
            label = f" -- {self.t(f'ui.inventory.categories.{category}')} "
            lines.append(self.color(label.ljust(self.width - 8, "-"), colors.LIGHT_GRAY))
            for e in group:
                line = f"    {number}. {self._item_name(e.item_id)}"
                lines.append(self.color(line, colors.GREEN) if e.item_id == selected_id else line)
                number += 1
            lines.append("")

        self.box(
            lines,
            header=self.t("ui.dev_mode.title"),
            footer=self.t("ui.catalog.count", count=len(entries)),
        )

        if self.view.selected is not None:
            print()
            self.box(self._detail_lines(self.view.selected), title=self._item_name(selected_id))

    def ask(self):
        options = [
            (self.t("ui.catalog.select"), self._ask_item),
            (self.t("ui.catalog.close"), CloseCatalog()),
        ]
        while True:
            action = self.choose(options)
            if action is not None:      # None = sélection annulée, on réaffiche le menu
                return action

    def _ask_item(self):
        """Demande le numéro d'un objet du cadre ; None si la saisie est vide."""
        entries = self.sorted_entries()
        while True:
            raw = self.ask_text(self.t("ui.catalog.prompt"))
            if not raw:
                return None
            if raw.isdigit() and 1 <= int(raw) <= len(entries):
                return InspectCatalogItem(entries[int(raw) - 1].item_id)
            print(self.t("ui.common.invalid_choice"))