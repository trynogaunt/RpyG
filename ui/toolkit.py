from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    # uniquement pour les hints, pas d'import runtime → pas de cycle
    from .ui_controller import UIController


def room_header(ui: "UIController", room_name: str, room_description: str) -> list[str]:
    # on utilise les méthodes de l'instance ui
    return ui.header(room_name) + ui.sub_header(room_description)