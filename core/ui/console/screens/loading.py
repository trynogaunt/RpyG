from core.boot import Boot, BootStep, StepStatus
from core.ui.console import colors
from core.ui.console.screens.base_screen import BaseConsoleScreen

STATUS_STYLE = {
    StepStatus.DONE: ("done", colors.GREEN),
    StepStatus.UNAVAILABLE: ("unavailable", colors.RED),
    StepStatus.TIMEOUT: ("timeout", colors.YELLOW),
}


class LoadingScreen(BaseConsoleScreen):
    """Affiché pendant `Boot.run()` : une ligne par étape, complétée quand l'étape se termine."""
    LABEL_WIDTH = 36

    def load(self, boot: Boot) -> None:
        self.render()
        boot.run(self.on_progress)

    def draw(self) -> None:
        self.rule()
        print()
        self.draw_splash()
        print()
        self.rule()
        print()
        self.centered(self.t("ui.loading.title"), colors.LIGHT_GRAY)
        print()

    def ask(self):
        raise NotImplementedError("L'écran de chargement n'attend aucune saisie")

    def on_progress(self, index: int, step: BootStep, status: StepStatus) -> None:
        if status is StepStatus.RUNNING:
            label = f"{self.t(f'ui.loading.steps.{step.key}')} "
            margin = " " * max((self.width - self.LABEL_WIDTH - 20) // 2, 2)
            print(margin + label.ljust(self.LABEL_WIDTH, "."), end=" ", flush=True)
            return
        key, code = STATUS_STYLE[status]
        print(self.color(f"[ {self.t(f'ui.loading.status.{key}')} ]", code), flush=True)
