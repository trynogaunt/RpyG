from ui.screens.abstract_screen import AbstractScreen
from ui import toolkit as tk
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ui.ui_controller import UIController
    from events.response import GameResponse

class SettingsScreen(AbstractScreen):
    def render(self, ui: "UIController", response: "GameResponse")-> List[str]:
        
        width = ui.width
        b_char = ui.border_char
        padding = ui.padding
        header_char = ui.header_char
        
        lines = []
        lines.extend(tk.header(ui.ctx.i18n.t("ui.settings.title"), width, b_char, header_char))
        lines.extend(tk.empty_line(count=2))
        lines.extend(tk.text_block(ui.ctx.i18n.t("ui.settings.options"), width, indent=1, border_char=b_char))
        return lines
    
    def display(self, lines: List[str]) -> None:
        print("\n".join(lines))