from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.items.effects.base import EffectContext, effect


def _valid_params(params: Mapping[str, Any]) -> bool:
    amount = params.get("amount")
    return isinstance(amount, int) and not isinstance(amount, bool) and amount > 0


@effect("heal", validate=_valid_params)
def heal(ctx: EffectContext, params: Mapping[str, Any]) -> bool:
    missing = ctx.player_max_health() - ctx.player_health()
    if missing <= 0:
        ctx.say("ui.messages.already_full_health")
        return False

    restored = min(params["amount"], missing)
    ctx.heal(restored)
    ctx.say("ui.messages.healed", amount=restored)
    return True