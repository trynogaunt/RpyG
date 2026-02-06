from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
import random
import logging

from game.locales.i18n import I18n

@dataclass
class GameContext:
    i18n = I18n()
    rng = random.Random()
    
    def t(self, key: str, *, count: Optional[int] = None, **kwargs: Any) -> str:
        return self.i18n.t(key, count=count, **kwargs)