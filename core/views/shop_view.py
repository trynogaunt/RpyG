from core.views.base_view import BaseView
from core.views.catalog_view import ItemDetailView
from dataclasses import dataclass

@dataclass(frozen=True)
class ShopItemView:
    """Une ligne  de stock"""
    item_id: str
    price: int
    affordable: bool

@dataclass(frozen=True)
class ShopView(BaseView):
    shop_id: str
    gold: int
    stock: tuple[ShopItemView, ...]
    free_slots: int = 0
    selected: ItemDetailView | None = None
    