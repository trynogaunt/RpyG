from textual.screen import Screen


class BaseScreen(Screen):
    def __init__(self, view=None):
        super().__init__()
        self._initial_view = view

    def on_mount(self) -> None:
        if self._initial_view is not None:
            self.update_view(self._initial_view)

    def update_view(self, view) -> None:
        pass

    def show_messages(self, messages: list[str]) -> None:
        pass