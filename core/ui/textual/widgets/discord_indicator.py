from textual.widgets import Static


class DiscordIndicator(Static):
    """Pastille « Discord » en haut à droite de l'écran, verte si la présence est active."""

    DEFAULT_CSS = """
    DiscordIndicator {
        dock: top;
        width: 100%;
        height: 1;
        content-align: right middle;
        padding: 0 1;
        color: $text-muted;
    }
    """

    def on_mount(self) -> None:
        self.refresh_status()

    def refresh_status(self) -> None:
        presence = self.app.presence
        if presence is None:
            self.display = False
            return
        if presence.connected:
            self.update(f"[green]●[/] {self.app.t('ui.discord.connected')}")
        else:
            self.update(f"[red]●[/] {self.app.t('ui.discord.disconnected')}")
