from ui.ui_controller import UIController
from game import game
import json
from pathlib import Path
from .locales.i18n import I18n
from game.game_context import GameContext
from integrations.discord_presence import DiscordPresence


def load_discord_presence() -> DiscordPresence | None:
    config_path = Path("config.json")
    if not config_path.exists():
        return None

    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    client_id = data.get("discord_client_id")
    if not client_id:
        return None

    presence = DiscordPresence(client_id)
    return presence

def main():
    ctx = GameContext(
        i18n=I18n(locale="fr", fallback_locale="en"),  # You can initialize this with your I18n instance if needed
    )
    game_ui = UIController(ctx=ctx, width=100, border_char="=", padding=4)
    game_instance = game.Game(ui=game_ui, ctx=ctx)
    discord = load_discord_presence()
    if discord:
        game_instance.discord_presence = discord
    game_instance.run()
    if discord:
        discord.close()
        
        
if __name__ == "__main__":
    main()
    