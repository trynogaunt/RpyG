from textual.screen import Screen
from dataclasses import dataclass, replace
import dataclasses


class BaseScreen(Screen):
    def __init__(self, view=None):
        super().__init__()
        self._initial_view = view

    def on_mount(self) -> None:
        self._translate_bindings()
        if self._initial_view is not None:
            self.update_view(self._initial_view)

    def _translate_bindings(self) -> None:
        self.log(self.app.t("ui.bindings.explore"))
        for key, bindings in self._bindings.key_to_bindings.items():
            self._bindings.key_to_bindings[key] = [
                dataclasses.replace(b, description=self.app.t(b.description))
                if b.description else b
                for b in bindings
            ]
        self.refresh_bindings()


    def update_view(self, view) -> None:
        pass

    def show_messages(self, messages: list[str]) -> None:
        pass