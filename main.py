from ui.ui_controller import UIController
from game import game
import json
from pathlib import Path
from game.locales.i18n import I18n
from models.game_context import GameContext
from models.settings import Settings, load_settings
from integrations.discord_presence import DiscordPresence
from time import sleep


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
    settings : Settings = load_settings()
    ctx : GameContext = GameContext(
        settings=settings,
        i18n=I18n(locale="en", fallback_locale="en")
    )
    print(settings.language)
    sleep(5)
    game_ui : UIController = UIController(ctx=ctx, width=settings.screen_width, border_char=settings.border_char, padding=settings.padding, header_char=settings.horizontal_char)
    game_instance : game.Game = game.Game(ui=game_ui, ctx=ctx)
    discord = load_discord_presence()
    if discord:
        game_instance.discord_presence = discord
    game_instance.run()
    if discord:
        discord.close()
        
        
if __name__ == "__main__":
    main()
    