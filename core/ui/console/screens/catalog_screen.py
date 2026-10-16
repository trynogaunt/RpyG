import unicodedata
from itertools import groupby

from core.ui.console.screens.base_screen import BaseConsoleScreen
from core.game.actions import CloseCatalog, InspectCatalogItem
from core.ui.console import colors
from core.updater import UpdateState
from core.version import __version__


def sort_key(text: str) -> str:
    """Clé de tri alphabétique sans casse ni accents (« Épée » rangée avec les « e »)."""
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


class CatalogScreen(BaseConsoleScreen):
    def sorted_entries(self):
        """Entrées groupées par catégorie, puis triées par nom traduit."""
        return sorted(
            self.view.entries,
            key=lambda e: (e.category or "", sort_key(self._item_name(e.item_id))),
        )

    def draw(self):
        entries = self.sorted_entries()
        lines = [""]
        number = 1
        for category, group in groupby(entries, key=lambda e: e.category):
            label = f" -- {self.t(f'ui.inventory.categories.{category}')} "
            lines.append(self.color(label.ljust(self.width - 8, "-"), colors.LIGHT_GRAY))
            for e in group:
                lines.append(f"    {number}. {self._item_name(e.item_id)}")
                number += 1
            lines.append("")

        self.box(
            lines,
            header=self.t("ui.dev_mode.title"),
            footer=self.t("ui.catalog.count", count=len(entries)),
        )

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