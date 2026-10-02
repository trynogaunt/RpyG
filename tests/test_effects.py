import pytest

import core.items.effects  # noqa: F401
from core.items.effects import base
from core.items.effects.base import (
    Effect,
    effect,
    get_effect,
    validate_item_effect,
)


class FakeContext:
    def __init__(self, health=5, max_health=10):
        self.health = health
        self.max_health = max_health
        self.heal_calls: list[int] = []
        self.messages: list[tuple[str, dict]] = []

    def player_health(self) -> int:
        return self.health

    def player_max_health(self) -> int:
        return self.max_health

    def heal(self, amount: int) -> None:
        self.heal_calls.append(amount)
        self.health = min(self.max_health, self.health + amount)

    def say(self, key: str, **params) -> None:
        self.messages.append((key, params))

@pytest.fixture
def empty_registry(monkeypatch):
    registry: dict[str, Effect] = {}
    monkeypatch.setattr(base, "EFFECTS", registry)
    return registry

def test_effect_decorator_registers_function(empty_registry):
    @effect("noop")
    def noop(ctx, params):
        return True

    assert "noop" in empty_registry
    assert empty_registry["noop"].name == "noop"
    assert empty_registry["noop"].apply is noop


def test_effect_decorator_returns_original_function(empty_registry):
    def fn(ctx, params):
        return True

    assert effect("same")(fn) is fn


def test_duplicate_effect_name_raises(empty_registry):
    @effect("dup")
    def first(ctx, params):
        return True

    with pytest.raises(ValueError):
        @effect("dup")
        def second(ctx, params):
            return True


def test_get_effect_unknown_raises(empty_registry):
    with pytest.raises(ValueError):
        get_effect("inexistant")


def test_get_effect_returns_registered(empty_registry):
    @effect("known")
    def known(ctx, params):
        return True

    assert get_effect("known") is empty_registry["known"]

def test_check_without_validator_accepts_anything():
    e = Effect(name="x", apply=lambda ctx, p: True)
    assert e.check({}) is True
    assert e.check({"nimporte": "quoi"}) is True


def test_check_uses_validator_result():
    e = Effect(name="x", apply=lambda ctx, p: True, validate=lambda p: p["ok"])
    assert e.check({"ok": True}) is True
    assert e.check({"ok": False}) is False


def test_check_returns_false_when_validator_raises():
    e = Effect(name="x", apply=lambda ctx, p: True, validate=lambda p: p["absent"])
    assert e.check({}) is False

def test_item_without_effect_is_valid(empty_registry):
    validate_item_effect("sword", None, {})   # ne doit pas lever


def test_item_with_unknown_effect_raises_with_item_id(empty_registry):
    with pytest.raises(ValueError, match="mystery_box"):
        validate_item_effect("mystery_box", "inconnu", {})


def test_item_with_invalid_params_raises_with_item_id(empty_registry):
    @effect("strict", validate=lambda p: p.get("n") == 1)
    def strict(ctx, params):
        return True

    with pytest.raises(ValueError, match="bad_item"):
        validate_item_effect("bad_item", "strict", {"n": 2})


def test_item_with_valid_effect_passes(empty_registry):
    @effect("strict", validate=lambda p: p.get("n") == 1)
    def strict(ctx, params):
        return True

    validate_item_effect("good_item", "strict", {"n": 1})


def test_heal_is_registered_by_importing_the_package():
    assert get_effect("heal").name == "heal"


@pytest.mark.parametrize("params", [{"amount": 1}, {"amount": 5}, {"amount": 999}])
def test_heal_accepts_positive_integer_amount(params):
    assert get_effect("heal").check(params) is True


@pytest.mark.parametrize(
    "params",
    [{}, {"amount": 0}, {"amount": -3}, {"amount": "5"}, {"amount": 2.5},
     {"amount": True}, {"amount": None}],
)
def test_heal_rejects_invalid_params(params):
    assert get_effect("heal").check(params) is False

def test_heal_restores_the_requested_amount():
    ctx = FakeContext(health=3, max_health=10)
    result = get_effect("heal").apply(ctx, {"amount": 4})
    assert result is True
    assert ctx.health == 7
    assert ctx.heal_calls == [4]


def test_heal_never_restores_more_than_missing_health():
    ctx = FakeContext(health=8, max_health=10)
    result = get_effect("heal").apply(ctx, {"amount": 5})
    assert result is True
    assert ctx.heal_calls == [2]
    assert ctx.health == 10


def test_heal_reports_the_amount_actually_restored():
    ctx = FakeContext(health=8, max_health=10)
    get_effect("heal").apply(ctx, {"amount": 5})
    assert ctx.messages == [("ui.messages.healed", {"amount": 2})]


def test_heal_is_refused_at_full_health():
    ctx = FakeContext(health=10, max_health=10)
    result = get_effect("heal").apply(ctx, {"amount": 5})
    assert result is False                    
    assert ctx.heal_calls == []
    assert ctx.messages == [("ui.messages.already_full_health", {})]


def test_heal_is_refused_when_health_exceeds_max():
    ctx = FakeContext(health=12, max_health=10)
    assert get_effect("heal").apply(ctx, {"amount": 5}) is False
    assert ctx.heal_calls == []