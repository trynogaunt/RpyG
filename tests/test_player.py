import pytest

from core.enums import Stat
from core.game.player import Player
from core.game.rules import STAT_RULES


@pytest.fixture
def fresh_player() -> Player:
    return Player(name="Test")


def test_new_player_starts_at_level_one(fresh_player):
    assert fresh_player.level == 1


def test_no_points_means_base_values(fresh_player):
    for stat, rule in STAT_RULES.items():
        assert fresh_player.get_stat(stat) == rule.base


@pytest.mark.parametrize("stat", list(STAT_RULES))
def test_one_point_adds_per_point(fresh_player, stat):
    boosted = Player(name="Test", allocated_points={stat: 1})
    gain = boosted.get_stat(stat) - fresh_player.get_stat(stat)
    assert gain == STAT_RULES[stat].per_point


@pytest.mark.parametrize("stat", list(STAT_RULES))
def test_points_only_affect_their_own_stat(fresh_player, stat):
    boosted = Player(name="Test", allocated_points={stat: 1})
    for other in STAT_RULES:
        if other is not stat:
            assert boosted.get_stat(other) == fresh_player.get_stat(other)


def test_level_two_adds_growth_per_level(fresh_player):
    before = {stat: fresh_player.get_stat(stat) for stat in STAT_RULES}
    fresh_player.level = 2
    for stat, rule in STAT_RULES.items():
        assert fresh_player.get_stat(stat) - before[stat] == rule.growth_per_level


def test_new_player_has_full_health():
    player = Player(name="Test", allocated_points={Stat.HEALTH: 3})
    assert player.health == player.max_health


def test_max_health_is_health_stat(fresh_player):
    assert fresh_player.max_health == fresh_player.get_stat(Stat.HEALTH)


def test_allocated_points_are_copied():
    points = {Stat.STRENGTH: 2}
    player = Player(name="Test", allocated_points=points)
    points[Stat.STRENGTH] = 99
    assert player.allocated_points[Stat.STRENGTH] == 2