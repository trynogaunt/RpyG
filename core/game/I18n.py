from pathlib import Path
import json

class Translation:
    def __init__(self, locales_dir: Path, locales: str, fallback: str = "en"):
        self.locale_file = locales
        self.fallback_file = fallback
        self.locales_dir = locales_dir

        self.translations = self._flatten(self.load_translation(self.locale_file))
        self.fallback_translations = self._flatten(self.load_translation(self.fallback_file))

    def load_translation(self, file_name: str) -> dict:
        with open(self.locales_dir / f"{file_name}.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def t(self, key: str, **params) -> str:
        text = self.translations.get(key)
        if text is None:
            text = self.fallback_translations.get(key, key)
        try:
            return text.format(**params)
        except (KeyError, IndexError):
            return text
    
    @staticmethod
    def _flatten(data: dict, prefix: str = "") -> dict[str, str]:
        flattened = {}
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flattened.update(Translation._flatten(value, full_key))
            else:
                flattened[full_key] = value
        return flattened
