from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol


class EffectContext(Protocol):
    def player_health(self) -> int: ...

    def player_max_health(self) -> int: ...

    def heal(self, amount: int) -> None: ...

    def say(self, key: str, **params: Any) -> None: ...


EffectFn = Callable[[EffectContext, Mapping[str, Any]], bool]
ParamsValidator = Callable[[Mapping[str, Any]], bool]


@dataclass(frozen=True)
class Effect:
    name: str
    apply: EffectFn
    validate: ParamsValidator | None = None

    def check(self, params: Mapping[str, Any]) -> bool:
        if self.validate is None:
            return True
        try:
            return bool(self.validate(params))
        except (KeyError, TypeError, ValueError):
            return False


EFFECTS: dict[str, Effect] = {}


def effect(name: str, *, validate: ParamsValidator | None = None):
    def register(fn: EffectFn) -> EffectFn:
        if name in EFFECTS:
            raise ValueError(f"Effect already registered : {name!r}")
        EFFECTS[name] = Effect(name=name, apply=fn, validate=validate)
        return fn

    return register


def get_effect(name: str) -> Effect:
    try:
        return EFFECTS[name]
    except KeyError:
        raise ValueError(f"Effet inconnu : {name!r}") from None


def validate_item_effect(item_id: str, effect_name: str | None,
                         params: Mapping[str, Any]) -> None:
    if effect_name is None:
        return
    found = EFFECTS.get(effect_name)
    if found is None:
        raise ValueError(f"{item_id} : unknown effect {effect_name!r}")
    if not found.check(params):
        raise ValueError(f"{item_id} : invalid parameters for {effect_name!r}")