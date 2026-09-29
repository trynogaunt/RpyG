from abc import ABC, abstractmethod
import shutil
import textwrap
from core.game.actions import Quit, NewGame, SetName
from core.ui.console import colors

class BaseConsoleScreen(ABC):
    def __init__(self, app, view=None):
        self.app = app
        self.view = view

   
    def update_view(self, view) -> None:
        self.view = view

    def render(self, messages=()) -> None:
        self.clear()
        self.draw()
        self.draw_messages(messages)

  
    @abstractmethod
    def draw(self) -> None: ...

    @abstractmethod
    def ask(self): ...          # -> Action

    # --- Outils communs ---
    def t(self, key, **params) -> str:
        return self.app.t(key, **params)

    @property
    def width(self) -> int:
        return shutil.get_terminal_size().columns

    def clear(self) -> None:
        print("\033[2J\033[H", end="")

    def draw_messages(self, messages) -> None:
        for message in messages:
            print(f"> {self.app.resolve_message(message)}")
    
    def choose(self, options: list[tuple[str, object | None]]):
        """options : liste de (libellé, action). Une action à None = option désactivée."""
        for i, (label, action) in enumerate(options, start=1):
            suffix = "" if action is not None else f" ({self.t('ui.common.unavailable')})"
            print(f"  {i}. {label}{suffix}")

        while True:
            try:
                raw = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                return Quit()
            if raw.isdigit() and 1 <= int(raw) <= len(options):
                action = options[int(raw) - 1][1]
                if action is not None:
                    return action() if callable(action) else action
            print(self.t("ui.common.invalid_choice"))
    
    def rule(self, char: str = "=") -> None:
        print(char * self.width)

    def centered(self, text: str, code: str = "") -> None:
        line = text.center(self.width)
        print(self.color(line, code) if code else line)

    def box(self, lines: list[str], footer: str | None = None,
            code: str = "", footer_code: str = "") -> None:
        inner = self.width - 4
        self.rule()
        for line in lines:
            for part in textwrap.wrap(line, inner) or [""]:
                cell = part.ljust(inner)
                print(f"| {self.color(cell, code) if code else cell} |")
        if footer:
            cell = footer.center(inner)
            print(f"| {self.color(cell, footer_code) if footer_code else cell} |")
        self.rule()
    
    def color(self, text: str, code: str) -> str:
        return f"{code}{text}{colors.RESET}"
    
    def ask_text(self, prompt: str) -> str:
        try:
            return input(f"{prompt} ").strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit

    def ask_name(self):
        name = self.ask_text(self.t("ui.creation.name_prompt"))
        return Quit() if name is None else SetName(name)
    
    def splash(self) -> list[str]:

        R = [
            "██████╗",
            "██╔══██╗",
            "██║  ██║",
            "██████╔╝",
            "██╔══██╗",
            "██║  ██║",
            "╚═╝  ╚═╝",
        ]

        P = [
            "██████╗",
            "██╔══██╗",
            "██████╔╝",
            "██╔═══╝ ",
            "██║     ",
            "██║     ",
            "╚═╝     ",
        ]

        Y = [
            "██╗   ██╗",
            "╚██╗ ██╔╝",
            " ╚████╔╝ ",
            "  ╚██╔╝  ",
            "   ██║   ",
            "   ██║   ",
            "   ╚═╝   ",
        ]

        G = [
            " ██████╗",
            "██╔════╝",
            "██║  ███╗",
            "██║   ██║",
            "██║   ██║",
            "╚██████╔╝",
            " ╚═════╝ ",
        ]

        return [R, P, Y, G]


    LETTER_COLORS = [colors.LIGHT_GRAY, colors.YELLOW, colors.YELLOW, colors.LIGHT_GRAY]  # R, P, Y, G (tuples RGB)


    def draw_splash(self) -> None:
        letters = self.splash()
        widths = [max(len(line) for line in letter) for letter in letters]
        gap = "  "
        total = sum(widths) + len(gap) * (len(letters) - 1)
        margin = " " * max((self.width - total) // 2, 0)

        for row in range(7):
            parts = [
                self.color(letter[row].ljust(width), rgb)
                for letter, width, rgb in zip(letters, widths, self.LETTER_COLORS)
            ]
            print(margin + gap.join(parts))