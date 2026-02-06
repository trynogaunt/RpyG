from ui import toolkit as tk
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ui.ui_controller import UIController
    from events.response import GameResponse

def render(ui: "UIController", response: "GameResponse")-> List[str]:
    width = ui.width
    b_char = ui.border_char
    padding = ui.padding
    header_char = ui.header_char
    lines = []
    lines.extend(tk.header(ui.ctx.i18n.t("ui.main_menu.title"), width, b_char, header_char))
    lines.extend(tk.empty_line(count=2))
    lines.extend(tk.splash(width, b_char))
    intro_text = ui.ctx.i18n.t("ui.main_menu.prompt_start")
    version_info = tk.color_text(ui.ctx.i18n.t("ui.main_menu.version_info"), tk.Colors.LIGHT_GRAY.value)
    lines.extend(tk.bottom_bar(width, header_char))
    lines.extend(tk.text_block(intro_text, width, indent=1, border_char=b_char))
    lines.extend(tk.empty_line(count=2, width=width, border_char=b_char))
    lines.extend(tk.center_text(version_info, width, b_char))
    lines.extend(tk.bottom_bar(width, header_char))
    lines.extend(tk.empty_line(count=2))
    return lines