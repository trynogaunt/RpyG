from itertools import groupby

from rich.text import Text
from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, OptionList, Static
from textual.widgets.option_list import Option

from core.game.actions import CloseCatalog, InspectCatalogItem
from core.ui.text_sort import sort_key
from core.ui.textual.screens.base_screen import BaseScreen
from core.ui.textual.widgets.item_detail import detail_markup
from core.views.catalog_view import CatalogView


class CatalogScreen(BaseScreen):
    """Mode dev : tous les objets groupés par catégorie, fiche de l'objet surligné à droite."""

    BINDINGS = [
        Binding("escape", "close", "ui.catalog.close"),
    ]

    def __init__(self, view: CatalogView | None = None, **kwargs):
        super().__init__(view=view, **kwargs)
        self.view = view
        self._built = False

    def compose(self):
        with Horizontal(id="cat-main"):
            with Vertical(id="cat-list-panel", classes="panel"):
                yield OptionList(id="cat-list", classes="inv-list")
            with Vertical(id="cat-detail-panel", classes="panel"):
                yield Static(id="cat-detail")
        yield Footer()

    # ----- rendu -----

    def update_view(self, view: CatalogView) -> None:
        self.view = view
        if not self._built:               # la liste ne change pas : construite une seule fois
            self._build_list()
            self._built = True
        self._render_detail()

    def _build_list(self) -> None:
        t = self.app.t
        panel = self.query_one("#cat-list-panel")
        panel.border_title = t("ui.dev_mode.title")
        panel.border_subtitle = t("ui.catalog.count", count=len(self.view.entries))

        entries = sorted(
            self.view.entries,
            key=lambda e: (e.category or "", sort_key(self._item_name(e.item_id))),
        )
        options = []
        for category, group in groupby(entries, key=lambda e: e.category):
            if options:
                options.append(None)      # séparateur entre deux catégories
            options.append(Option(Text.from_markup(
                f"[bold #ffb000]{t(f'ui.inventory.categories.{category}')}[/]"), disabled=True))
            options += [Option(f"  {self._item_name(e.item_id)}", id=e.item_id) for e in group]

        lst = self.query_one("#cat-list", OptionList)
        with self.prevent(OptionList.OptionHighlighted):
            lst.add_options(options)
        selected = self.view.selected.item_id if self.view.selected else None
        start = next((i for i, o in enumerate(options) if o is not None and not o.disabled
                      and (selected is None or o.id == selected)), None)
        if start is not None:
            lst.highlighted = start       # déclenche OptionHighlighted -> affiche la fiche
        lst.focus()

    def _render_detail(self) -> None:
        panel = self.query_one("#cat-detail-panel")
        detail = self.query_one("#cat-detail", Static)
        d = self.view.selected
        if d is None:
            panel.border_title = ""
            detail.update("")
            return
        panel.border_title = self._item_name(d.item_id)
        detail.update(detail_markup(self.app.t, d))

    def _item_name(self, item_id: str) -> str:
        return self.app.t(f"items.{item_id}.name")

    # ----- navigation -----

    @on(OptionList.OptionHighlighted, "#cat-list")
    def _on_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        item_id = event.option.id
        current = self.view.selected.item_id if self.view.selected else None
        if item_id is not None and item_id != current:
            self.app.dispatch(InspectCatalogItem(item_id))

    def action_close(self) -> None:
        self.app.dispatch(CloseCatalog())
