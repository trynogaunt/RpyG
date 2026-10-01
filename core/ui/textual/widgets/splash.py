from rich.text import Text
from core.ui import splash

LETTER_STYLES = ["#c5cdd9", "#ffb000", "#ffb000", "#c5cdd9"]  # R, P, Y, G

def build_splash() -> Text:
    text = Text(no_wrap=True, justify="center")
    for i, row in enumerate(splash.rows()):
        if i:
            text.append("\n")
        for j, (part, style) in enumerate(zip(row, LETTER_STYLES)):
            if j:
                text.append("  ")
            text.append(part, style=style)
    return text