from dataclasses import dataclass
from .base_view import BaseView
from .inventory_view import ItemDetailView

@dataclass(frozen=True)
class CatalogEntryView:
    item_id: str    
    category: str | None

@dataclass(frozen=True)
class CatalogView(BaseView):
    entries: tuple[CatalogEntryView, ...]
    selected: ItemDetailView | None = None