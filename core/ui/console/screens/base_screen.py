from abc import ABC, abstractmethod
import shutil
from core.game.actions import Quit, NewGame, SetName

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

    def centered(self, text: str) -> None:
        print(text.center(self.width))
    
    def ask_text(self, prompt: str) -> str:
        try:
            return input(f"{prompt} ").strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit

    def ask_name(self):
        name = self.ask_text(self.t("ui.creation.name_prompt"))
        return Quit() if name is None else SetName(name)