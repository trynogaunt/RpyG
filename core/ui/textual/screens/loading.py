from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import ProgressBar, Static

from core.boot import Boot, BootStep, StepStatus
from core.ui.textual.widgets.splash import build_splash

# icône, style, clé de statut affichée à côté du libellé
STATUS_STYLE = {
    StepStatus.RUNNING: ("◌", "#ffb000", None),
    StepStatus.DONE: ("✓", "green", None),
    StepStatus.UNAVAILABLE: ("✗", "red", "unavailable"),
    StepStatus.TIMEOUT: ("◷", "#ffb000", "timeout"),
}


class LoadingScreen(Screen):
    """Exécute `Boot.run()` dans un thread et affiche la progression, puis lance le jeu."""

    DEFAULT_CSS = """
    LoadingScreen { align: center middle; }
    LoadingScreen #loading-splash { width: auto; margin-bottom: 2; }
    LoadingScreen #loading-box { width: 56; height: auto; border: round $accent; padding: 1 2; }
    LoadingScreen #loading-title { width: 100%; text-align: center; text-style: bold; }
    LoadingScreen #loading-bar { margin: 1 0; }
    LoadingScreen .loading-step { color: $text-muted; }
    """

    def __init__(self, boot: Boot):
        super().__init__()
        self.boot = boot
        self.steps = boot.steps()

    def compose(self) -> ComposeResult:
        with Center():
            yield Static(build_splash(), id="loading-splash")
        with Center():
            with Vertical(id="loading-box"):
                yield Static(self.app.t("ui.loading.title"), id="loading-title")
                yield ProgressBar(total=len(self.steps), show_eta=False, id="loading-bar")
                for step in self.steps:
                    yield Static(f"·  {self._label(step)}", id=f"step-{step.key}", classes="loading-step")

    def on_mount(self) -> None:
        self.run_worker(self._load, thread=True, exclusive=True)

    def _load(self) -> None:
        self.boot.run(lambda i, step, status: self.app.call_from_thread(self._progress, step, status))
        self.app.call_from_thread(self.app.start_game)

    def _label(self, step: BootStep) -> str:
        return self.app.t(f"ui.loading.steps.{step.key}")

    def _progress(self, step: BootStep, status: StepStatus) -> None:
        icon, style, status_key = STATUS_STYLE[status]
        text = f"[{style}]{icon}[/]  {self._label(step)}"
        if status_key:
            text += f"  [dim]({self.app.t(f'ui.loading.status.{status_key}').lower()})[/]"
        self.query_one(f"#step-{step.key}", Static).update(text)
        if status is not StepStatus.RUNNING:
            self.query_one("#loading-bar", ProgressBar).advance(1)
