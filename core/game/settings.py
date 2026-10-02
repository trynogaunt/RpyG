# core/settings.py
import json
from dataclasses import dataclass, field, fields
from pathlib import Path

from platformdirs import user_config_path


def default_settings_path() -> Path:
    return user_config_path("rpyg") / "settings.json"


@dataclass
class Settings:
    locale: str = "en"
    interface: str = "console"
    available_locales: list[str] = field(default_factory=lambda: ["fr", "en", "es", "de"])
    available_interfaces: list[str] = field(default_factory=lambda: ["console", "textual"])
    controls: str = "keyboard"
    discord_integration: bool = False

    path: Path | None = field(default=None, init=False, repr=False, compare=False)

    @classmethod
    def _persisted_fields(cls) -> set[str]:
        return {f.name for f in fields(cls) if f.init}

    @classmethod
    def load(cls, path: Path) -> "Settings":
        raw = {}
        try:
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, OSError):
            pass  # fichier illisible → valeurs par défaut

        if not isinstance(raw, dict):
            raw = {}

        known = cls._persisted_fields()
        settings = cls(**{k: v for k, v in raw.items() if k in known})
        settings.path = path
        return settings

    def to_dict(self) -> dict:
        return {name: getattr(self, name) for name in self._persisted_fields()}

    def save(self) -> None:
        if self.path is None:
            raise ValueError("Settings has no path, use Settings.load(path)")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        tmp.replace(self.path)