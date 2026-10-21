from abc import ABC, abstractmethod
import re
import shutil
import textwrap
from core.game.actions import Back, Quit, NewGame, SetName
from core.ui.console import colors

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def visible_len(s: str) -> int:
    """Longueur affichée, sans les codes couleur."""
    return len(ANSI.sub("", s))


def pad(s: str, width: int) -> str:
    return s + " " * max(0, width - visible_len(s))


def fit(s: str, width: int) -> str:
    """Coupe un texte sans couleur trop long ; un texte coloré est supposé déjà à la bonne taille."""
    if visible_len(s) <= width or ANSI.search(s):
        return s
    return s[: width - 1] + "…"

MIN_COLUMN = 28        # en dessous, columns() empile les deux colonnes


class BaseConsoleScreen(ABC):
    def __init__(self, app, view=None):
        self.app = app
        self.view = view

   
    def update_view(self, view) -> None:
        self.view = view

    def render(self, messages=()) -> None:
        self.clear()
        self.draw()
        self.draw_status()
        self.draw_messages(messages)
        print()

    def draw_status(self) -> None:
        """Ligne d'état en bas à droite : liaison Discord, si l'intégration est activée."""
        presence = getattr(self.app, "presence", None)
        if presence is None:
            return
        key, code = ("connected", colors.GREEN) if presence.connected else ("disconnected", colors.RED)
        text = self.t(f"ui.discord.{key}")
        print(" " * max(self.width - len(text) - 1, 0) + self.color(text, code))

  
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
    
    BACK_KEY = "0"

    def choose(self, options: list[tuple[str, object | None]]):
        """options : liste de (libellé, action). Une action à None = option désactivée.

        L'option de sortie (`Back()`, sinon `Quit()`) est toujours affichée en dernier sur la touche 0 ;
        les autres sont numérotées à partir de 1.
        """
        back = next((option for option in options if isinstance(option[1], Back)), None) \
            or next((option for option in options if isinstance(option[1], Quit)), None)
        numbered = [option for option in options if option is not back]

        for i, (label, action) in enumerate(numbered, start=1):
            suffix = "" if action is not None else f" ({self.t('ui.common.unavailable')})"
            print(f"  {i}. {label}{suffix}")
        if back:
            print(f"  {self.BACK_KEY}. {back[0]}")

        while True:
            try:
                raw = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                return Quit()
            if back and raw == self.BACK_KEY:
                return back[1]
            if raw.isdigit() and 1 <= int(raw) <= len(numbered):
                action = numbered[int(raw) - 1][1]
                if action is not None:
                    return action() if callable(action) else action
            print(self.t("ui.common.invalid_choice"))
    
    def rule(self, char: str = "=") -> None:
        print(char * self.width)

    def centered(self, text: str, code: str = "") -> None:
        line = text.center(self.width)
        print(self.color(line, code) if code else line)
    
    def column_widths(self) -> tuple[int, int] | None:
        """Largeurs des deux colonnes d'un box(), ou None si le terminal est trop étroit."""
        inner = self.width - 4
        left = (inner - 3) // 2
        right = inner - 3 - left
        return (left, right) if left >= MIN_COLUMN else None

    def columns(self, left: list[str], right: list[str]) -> list[str]:
        """Lignes de box() en deux colonnes séparées par « | » ; empilées si le terminal est trop étroit."""
        widths = self.column_widths()
        if widths is None:
            return left + [""] + right
        left_w, right_w = widths
        rows = max(len(left), len(right))
        left, right = left + [""] * (rows - len(left)), right + [""] * (rows - len(right))
        return [pad(fit(l, left_w), left_w) + " | " + fit(r, right_w) for l, r in zip(left, right)]

    def column_rule(self) -> str:
        """Ligne de box() qui ferme les deux colonnes : -----+-----."""
        widths = self.column_widths()
        if widths is None:
            return "-" * (self.width - 4)
        left_w, right_w = widths
        return "-" * left_w + "-+-" + "-" * right_w

    def empty_line_box(self) -> None:
        print(f"| {' ' * (self.width - 4)} |")

    def box(self, lines: list[str], footer: str | None = None, header: str | None = None, title: str | None = None,
        code: str = "", footer_code: str = "") -> None:
        inner = self.width - 4
        
        if header:
            label = f" {header} "
            left = (self.width - len(label)) // 2
            right = self.width - len(label) - left
            label = self.color(label, code) if code else label
            print("=" * left + label + "=" * right)
        else:
            self.rule()

        if title:
            title = title[: self.width - 8]
            label = f" {title} "
            left = 2
            right = self.width - left - len(label)
            label = self.color(label, code) if code else label
            print("|" + label + " " * (right) + "|")
            self.empty_line_box()


        for line in lines:
            # Une ligne courte (éventuellement colorée) est gardée telle quelle, indentation comprise
            fits = "\n" not in line and visible_len(line) <= inner and line.strip()
            for part in [line] if fits else textwrap.wrap(line, inner) or [""]:
                cell = pad(part, inner)
                print(f"| {self.color(cell, code) if code else cell} |")

        if footer:
            label = f" {footer} "
            left = (self.width - len(label)) // 2
            right = self.width - len(label) - left
            label = self.color(label, footer_code) if footer_code else label
            print("=" * left + label + "=" * right)
        else:
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
    
    def _item_name(self, item_id: str) -> str:
        return self.t(f"items.{item_id}.name")