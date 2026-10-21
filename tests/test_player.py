import pytest

from core.enums import Stat
from core.game.player import Player
from core.game.rules import LEVEL_XP, STAT_RULES


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

# ----- expérience et niveaux -----


def test_new_player_has_no_xp(fresh_player):
    assert (fresh_player.xp, fresh_player.xp_next) == (0, LEVEL_XP[1])


def test_xp_below_threshold_keeps_level(fresh_player):
    assert fresh_player.gain_xp(LEVEL_XP[1] - 1) == 0
    assert fresh_player.level == 1


def test_reaching_threshold_levels_up_and_adds_the_health_gained(fresh_player):
    fresh_player.health = 4
    assert fresh_player.gain_xp(LEVEL_XP[1]) == 1
    assert fresh_player.level == 2
    assert fresh_player.health == 4 + STAT_RULES[Stat.HEALTH].growth_per_level
    assert fresh_player.xp_next == LEVEL_XP[2]


def test_big_gain_climbs_several_levels(fresh_player):
    assert fresh_player.gain_xp(LEVEL_XP[3]) == 3
    assert fresh_player.level == 4


def test_level_is_capped_but_xp_keeps_counting(fresh_player):
    fresh_player.gain_xp(LEVEL_XP[-1] + 500)
    assert fresh_player.level == len(LEVEL_XP)
    assert fresh_player.xp_next is None
    assert fresh_player.xp == LEVEL_XP[-1] + 500
