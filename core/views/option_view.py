from dataclasses import dataclass
from .base_view import BaseView

@dataclass(frozen=True)
class OptionView(BaseView):
    locale: str
    available_locales: list[str]
    interface: str
    available_interfaces: list[str]
    controls: str