from dataclasses import dataclass

import pytest

from core.game.effect import EFFECTS, heal, register_effect
from core.game.player import Player


@dataclass
class Dummy:
    """Cible minimale qui respecte HasHealth, sans être un Player."""
    health: int
    max_health: int = 10


def test_heal_is_registered():
    assert EFFECTS["heal"] is heal


def test_heal_adds_amount():
    target = Dummy(health=3)
    heal(5, target)
    assert target.health == 8


def test_heal_is_capped_at_max_health():
    target = Dummy(health=8)
    heal(5, target)
    assert target.health == 10


@pytest.mark.parametrize("amount", [0, -3])
def test_heal_rejects_non_positive_amount(amount):
    target = Dummy(health=3)
    with pytest.raises(ValueError):
        heal(amount, target)
    assert target.health == 3


def test_heal_works_on_player():
    player = Player("Bob")
    player.health = 1
    heal(5, player)
    assert player.health == 6


def test_register_effect_returns_function_unchanged():
    def boost(amount, target):
        return amount

    try:
        assert register_effect("test_boost")(boost) is boost
        assert EFFECTS["test_boost"] is boost
    finally:
        EFFECTS.pop("test_boost", None)
