from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class Settings():
    """Settings for the game."""
    # Whether to show the title screen at the start of the game.
    show_title_screen: bool = True
    language: str = "en"
    screen_width: int = 100
    padding: int = 1
    border_char : str = "|"
    horizontal_char : str = "="
    sub_title_char : str = "-"
    split_char : str = "#"
    
def load_settings() -> Settings:
    """Load settings from a JSON file."""
    config_path = Path("settings.json")
    if not config_path.exists():
        print("No settings file found. Using default settings.")
        return Settings()

    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not isinstance(data, dict) or data is None:
        print("Invalid settings file format. Using default settings.")
        return Settings()

    print("Settings loaded successfully.")
    ui_settings = data.get("ui", {})
    return Settings(
        show_title_screen=data.get("show_title_screen", True),
        language=data.get("language", "en"),
        screen_width=ui_settings.get("screen_width", 80),
        padding=ui_settings.get("padding", 1),
        border_char=ui_settings.get("border_char", "|"),
        horizontal_char=ui_settings.get("horizontal_char", "="),
        sub_title_char=ui_settings.get("sub_title_char", "-"),
        split_char=ui_settings.get("split_char", "#")
    )