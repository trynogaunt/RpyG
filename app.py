from ui.screens.main_menu_screen import splash, main_menu_choice
from ui.ui_controller import UIController
from classes.hero import Hero
from game import creation_flow, game
from integrations import discord_presence
import questionary
import json
from pathlib import Path
from integrations.discord_presence import DiscordPresence
def load_discord_presence() -> discord_presence.DiscordPresence | None:
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
    hero = None
    ui = UIController(width=80, border_char="=", padding=2)
    splash_lines = splash()
    ui.render(splash_lines, tick_render=0.05)
    choice = main_menu_choice()
    if choice == "Start New Game":
        hero = creation_flow.create_character(ui)
    elif choice == "Settings":
        pass
    elif choice == "Load Game":
        pass
    elif choice == "Exit":
        print("Exiting the game. Goodbye!")

    if hero:
        start_adventure = questionary.confirm("Start your adventure now?").ask()
    else:
        print("No character created.")

    if hero and start_adventure:
        presence = load_discord_presence()
        game_instance = game.Game(ui, hero)
        game_instance.discord_presence = presence
        game_instance.run()
        presence.clear() 
if __name__ == "__main__":
    main()
    