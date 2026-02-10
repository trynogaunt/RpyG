from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from models.settings import Settings
import random
import logging


from game.locales.i18n import I18n

class GameContext():
    def __init__(self, settings: Settings, i18n: Optional[I18n] = None):
        self.rng = random.Random()
        self.settings = settings
        self.i18n = I18n(locale=self.settings.language, fallback_locale="en")
        print(f"GameContext initialized with language: {self.settings.language}")
        print(f"{self.i18n.locale=}, {self.i18n.fallback_locale=}")
    def t(self, key: str, *, count: Optional[int] = None, **kwargs: Any) -> str:
        return self.i18n.t(key, count=count, **kwargs)