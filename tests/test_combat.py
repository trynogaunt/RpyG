from random import Random

import pytest

from core.enemies.base import Enemy
from core.enemies.catalog import EnemyCatalog
from core.enums import Screens, Stat
from core.game.actions import AttackEnemy, Flee, Quit, StartCombat
from core.combat.fighters import Combatant, PlayerFighter
from core.combat.resolution import (BLOCK_CAP, CRIT_CAP, Hit, armor_ratio, block_chance, crit_chance, finalize,
                                    resolve_attack)
from core.combat.moves import Strike
from core.combat.rewards import xp_gain
from core.combat.state import CombatLogEntry, CombatState, Outcome
from core.game.response import Message
from core.game.rules import LEVEL_XP
from core.game.game import Game
from core.game.inventory import Equipped
from core.game.player import Player
from core.items.base import Attack, Defense, Item, ItemInstance, Slot
from core.items.catalog import ItemCatalog
from core.views.combat_view import FoeView
from core.views.exploration_view import EncounterView
from core.world.models import Encounter, EncounterRef, Room, RoomRef, World, Zone

DEN = RoomRef("cave", "den")
HALL = RoomRef("cave", "hall")


class FixedRolls(Random):
    """Jets imposés : random() renvoie les valeurs données, puis 0.99 (aucun crit)."""

    def __init__(self, *rolls: float):
        super().__init__()
        self.rolls = list(rolls)

    def random(self) -> float:
        return self.rolls.pop(0) if self.rolls else 0.99


def enemy(enemy_id: str, health: int, strength: int, attack: Attack = Attack(), speed: int = 1, xp: int = 0,
          level: int = 1) -> Enemy:
    return Enemy(id=enemy_id, stats={Stat.HEALTH: health, Stat.STRENGTH: strength, Stat.SPEED: speed, Stat.LUCK: 1},
                 attack=attack, xp=xp, level=level)


def fighter() -> PlayerFighter:
    """Joueur à mains nues, sans armure ni bouclier."""
    return PlayerFighter(player=Player("Bob"), attack=Attack(), wear=1.0, armor=0, block=0.0)


@pytest.fixture
def game() -> Game:
    """Joueur (PV 10, force 5, à mains nues) dans une salle avec un rat (PV 12, force 3)."""
    cave = Zone(id="cave", name="Grotte", description="", entry_room="den", rooms={
        "den": Room("Tanière", "", DEN, encounters=(Encounter("rat", ("rat",)), Encounter("ogre", ("ogre",)),
                                                   Encounter("wolf", ("wolf",)),
                                                   Encounter("pack", ("rat", "rat", "wolf")),
                                                   Encounter("nest", ("rat",), respawn=True))),
        "hall": Room("Salle", "", HALL),
    })
    g = Game(
        world=World(start=DEN, zones={"cave": cave}),
        enemies=EnemyCatalog({"rat": enemy("rat", 12, 3, xp=8), "ogre": enemy("ogre", 50, 20), "bat": enemy("bat", 5, 1),
                              "wolf": enemy("wolf", 30, 2, speed=9)}),
        catalog=ItemCatalog({"club": Item(id="club", category="weapons", slots=((Slot.RIGHT_HAND,),),
                                          attack=Attack(damage_multiplier=2.0))}),
        rng=FixedRolls(),
    )
    g.start()
    g.player = Player("Bob", location=DEN)
    g.screen = Screens.EXPLORATION
    return g


def message_keys(response) -> list[str]:
    return [m.key for m in response.messages]


# ----- formule -----

@pytest.mark.parametrize("damage, roll, expected", [
    (2.7, 0.69, 3),      # jet sous la partie décimale : arrondi vers le haut
    (2.7, 0.70, 2),      # sinon vers le bas
    (0.2, 0.99, 1),      # un coup qui touche fait au moins 1
])
def test_finalize_rounds_stochastically(damage, roll, expected):
    assert finalize(damage, FixedRolls(roll)) == expected


def test_finalize_whole_damage_needs_no_roll():
    rng = FixedRolls(0.0)
    assert finalize(5.0, rng) == 5
    assert finalize(10.000000000000002, rng) == 10   # bruit des floats ignoré
    assert finalize(0, rng) == 0
    assert rng.rolls == [0.0]                        # aucun jet consommé


def test_finalize_matches_real_damage_on_average():
    rng = Random(42)
    rolls = [finalize(2.7, rng) for _ in range(10_000)]
    assert sum(rolls) / len(rolls) == pytest.approx(2.7, abs=0.02)


@pytest.mark.parametrize("armor, expected", [(0, 1.0), (25, 0.8), (100, 0.5), (300, 0.25)])
def test_armor_ratio_has_diminishing_returns(armor, expected):
    assert armor_ratio(armor) == pytest.approx(expected)


def test_armor_reduces_each_hit():
    hits = resolve_attack(10, 0, Attack(hits=2), 1.0, 100, 0.0, FixedRolls())     # 10 x 0.5 = 5 par coup
    assert [h.damage for h in hits] == [5, 5]


@pytest.mark.parametrize("base, wear, speed, luck, expected", [
    (0.05, 1.0, 5, 1, 0.05 * (1 + 2 * 5.5 / 25.5)),     # bouclier en bois au départ : ~7 %
    (0.05, 0.5, 5, 1, 0.025 * (1 + 2 * 5.5 / 25.5)),    # usé à moitié : divisé par deux
    (0.0, 1.0, 100, 100, 0.0),                           # sans bouclier, les stats ne suffisent pas
])
def test_block_chance(base, wear, speed, luck, expected):
    assert block_chance(base, wear, speed, luck) == pytest.approx(expected)


def test_stats_never_triple_the_shield():
    assert block_chance(0.05, 1.0, 10_000, 10_000) < 0.15


def test_block_chance_is_capped():
    assert block_chance(0.5, 1.0, 100, 100) == BLOCK_CAP


def test_blocked_hit_deals_nothing_and_skips_crit_roll():
    attack = Attack(hits=2, crit_chance=1.0, crit_multiplier=2.0)
    hits = resolve_attack(10, 0, attack, 1.0, 0, 0.2, FixedRolls(0.1, 0.5, 0.0))   # bloqué, puis non bloqué + crit
    assert hits == [Hit(damage=0, crit=False, blocked=True), Hit(damage=20, crit=True)]


def test_negative_armor_is_rejected():
    with pytest.raises(ValueError):
        Defense(armor=-1)


@pytest.mark.parametrize("wear, luck, expected", [
    (1.0, 0, 0.20),      # arme neuve, sans Chance
    (0.5, 0, 0.10),      # usée à moitié : crit divisé par deux
    (0.0, 0, 0.0),       # complètement usée : plus de crit
    (1.0, 10, 0.26),     # 10 de Chance : x1.3
])
def test_crit_chance(wear, luck, expected):
    assert crit_chance(Attack(crit_chance=0.2), wear, luck) == pytest.approx(expected)


def test_luck_cannot_create_crit_from_nothing():
    assert crit_chance(Attack(crit_chance=0.0), 1.0, 100) == 0.0


def test_crit_chance_is_capped():
    assert crit_chance(Attack(crit_chance=0.8), 1.0, 100) == CRIT_CAP


def test_each_hit_rolls_its_own_crit():
    attack = Attack(damage_multiplier=0.6, hits=2, crit_chance=0.5, crit_multiplier=2.0)
    hits = resolve_attack(10, 0, attack, 1.0, 0, 0.0, FixedRolls(0.1, 0.9))     # 1er coup crit, pas le 2e
    assert [(h.damage, h.crit) for h in hits] == [(12, True), (6, False)]


# ----- exemplaires -----


def test_spawn_starts_at_full_health():
    rat = enemy("rat", 12, 3)
    assert Combatant.spawn(rat) == Combatant(enemy=rat, health=12)


@pytest.mark.parametrize("damage, expected", [(5, 7), (12, 0), (50, 0)])
def test_take_damage_never_goes_below_zero(damage, expected):
    foe = Combatant.spawn(enemy("rat", 12, 3))
    foe.take_damage(damage)
    assert foe.health == expected
    assert foe.alive == (expected > 0)


def test_same_enemy_twice_gives_independent_copies():
    rat = enemy("rat", 12, 3)
    combat = CombatState.start(fighter(), [rat, rat])
    combat.foes[0].take_damage(5)
    assert [f.health for f in combat.foes] == [7, 12]
    assert combat.foes[0].enemy is combat.foes[1].enemy     # la définition reste partagée


def test_living_skips_dead_foes_and_keeps_order():
    combat = CombatState.start(fighter(), [enemy("rat", 12, 3), enemy("bat", 5, 1), enemy("wolf", 30, 2)])
    combat.foes[1].take_damage(5)
    assert [f.enemy.id for f in combat.living] == ["rat", "wolf"]


def test_defeated_only_when_every_foe_is_down():
    combat = CombatState.start(fighter(), [enemy("rat", 12, 3), enemy("bat", 5, 1)])
    combat.foes[0].take_damage(12)
    assert not combat.defeated
    combat.foes[1].take_damage(5)
    assert combat.defeated


def test_cannot_start_combat_without_enemies():
    with pytest.raises(ValueError):
        CombatState.start(fighter(), [])


def test_every_living_foe_strikes_once_per_round():
    rat = enemy("rat", 12, 3)
    combat = CombatState.start(fighter(), [rat, rat])
    assert combat.play_round(Strike(0), FixedRolls()) is Outcome.ONGOING
    assert combat.log == [CombatLogEntry("player", 5, foe=0), CombatLogEntry("enemy", 3, foe=0),
                          CombatLogEntry("enemy", 3, foe=1)]
    assert combat.player.player.health == 10 - 6


def test_foe_killed_before_its_turn_does_not_strike():
    combat = CombatState.start(fighter(), [enemy("bat", 5, 1), enemy("rat", 12, 3)])
    combat.play_round(Strike(0), FixedRolls())
    assert combat.log == [CombatLogEntry("player", 5, foe=0), CombatLogEntry("enemy", 3, foe=1)]


# ----- déroulement -----


def test_exploration_view_lists_room_encounters(game):
    assert game._exploration_to_view().encounters[3] == EncounterView("pack", (("rat", 2), ("wolf", 1)))
    assert [e.id for e in game._exploration_to_view().encounters] == ["rat", "ogre", "wolf", "pack", "nest"]


@pytest.mark.parametrize("encounter_id", ["bat", "ghost"], ids=["ennemi-hors-de-la-salle", "inconnue"])
def test_cannot_fight_encounter_not_in_room(game, encounter_id):
    response = game.handle_action(StartCombat(encounter_id))
    assert response.screen is Screens.EXPLORATION
    assert game.combat is None


def test_start_combat(game):
    response = game.handle_action(StartCombat("rat"))
    assert response.screen is Screens.COMBAT
    assert response.view.foes == (FoeView("rat", 12, 12),)
    assert response.view.log == ()


def test_start_combat_against_a_group(game):
    response = game.handle_action(StartCombat("pack"))
    assert response.view.foes == (FoeView("rat", 12, 12, tag="A"), FoeView("rat", 12, 12, tag="B"),
                                  FoeView("wolf", 30, 30))


def test_attack_then_enemy_strikes_back(game):
    game.handle_action(StartCombat("rat"))
    response = game.handle_action(AttackEnemy())
    assert response.view.foes[0].health == 12 - 5
    assert response.view.player_summary.health == 10 - 3
    assert response.view.log == (CombatLogEntry("player", 5), CombatLogEntry("enemy", 3))


def test_equipped_weapon_is_used(game):
    game.player.inventory.equipped.append(Equipped(slots=(Slot.RIGHT_HAND,), instance=ItemInstance("club")))
    game.handle_action(StartCombat("rat"))
    assert game.handle_action(AttackEnemy()).view.foes[0].health == 12 - 10


def test_equipped_armor_adds_up_against_enemy_hits(game):
    game.enemies = EnemyCatalog({"rat": enemy("rat", 12, 20)})
    game.catalog = ItemCatalog({
        "shield": Item(id="shield", category="shields", slots=((Slot.LEFT_HAND,),), defense=Defense(armor=60)),
        "helmet": Item(id="helmet", category="helmets", slots=((Slot.HEAD,),), defense=Defense(armor=40)),
    })
    game.player.inventory.equipped += [Equipped(slots=(Slot.LEFT_HAND,), instance=ItemInstance("shield", wear=1.0)),
                                       Equipped(slots=(Slot.HEAD,), instance=ItemInstance("helmet", wear=1.0))]
    game.player.allocated_points[Stat.HEALTH] = 10                  # PV 60, pour survivre au coup
    game.player.health = game.player.max_health
    game.handle_action(StartCombat("rat"))
    assert game.handle_action(AttackEnemy()).view.log[1] == CombatLogEntry("enemy", 10)   # 20 x 100/200


def test_enemy_armor_reduces_player_hits(game):
    game.enemies = EnemyCatalog({"rat": Enemy(id="rat", stats={Stat.HEALTH: 12, Stat.STRENGTH: 3, Stat.SPEED: 1,
                                                               Stat.LUCK: 1}, defense=Defense(armor=150))})
    game.handle_action(StartCombat("rat"))
    assert game.handle_action(AttackEnemy()).view.log[0] == CombatLogEntry("player", 2)   # 5 x 0.4


def test_shield_blocks_enemy_hit(game):
    game.rng = FixedRolls(0.99, 0.0)                                # crit du joueur raté, puis blocage du coup du rat
    game.catalog = ItemCatalog({"shield": Item(id="shield", category="shields", slots=((Slot.LEFT_HAND,),),
                                               defense=Defense(block_chance=0.05))})
    game.player.inventory.equipped.append(Equipped(slots=(Slot.LEFT_HAND,), instance=ItemInstance("shield", wear=1.0)))
    game.handle_action(StartCombat("rat"))
    response = game.handle_action(AttackEnemy())
    assert response.view.log[1] == CombatLogEntry("enemy", 0, blocked=True)
    assert response.view.player_summary.health == 10


def test_best_shield_is_used_not_the_sum(game):
    game.catalog = ItemCatalog({
        "small": Item(id="small", category="shields", slots=((Slot.LEFT_HAND,),), defense=Defense(block_chance=0.05)),
        "big": Item(id="big", category="shields", slots=((Slot.RIGHT_HAND,),), defense=Defense(block_chance=0.08)),
    })
    game.player.inventory.equipped += [Equipped(slots=(Slot.LEFT_HAND,), instance=ItemInstance("small", wear=1.0)),
                                       Equipped(slots=(Slot.RIGHT_HAND,), instance=ItemInstance("big", wear=1.0))]
    assert PlayerFighter.from_player(game.player, game.catalog).block == pytest.approx(block_chance(0.08, 1.0, 5, 1))


def test_victory_returns_to_exploration(game):
    game.handle_action(StartCombat("rat"))
    game.handle_action(AttackEnemy())
    game.handle_action(AttackEnemy())
    response = game.handle_action(AttackEnemy())          # 5 + 5 + 5 >= 12
    assert response.screen is Screens.EXPLORATION
    assert message_keys(response) == ["ui.combat.victory", "ui.combat.xp_gained"]
    assert game.combat is None
    assert game.player.health == 10 - 3 - 3               # le rat ne riposte pas au coup fatal


def test_flee(game):
    game.handle_action(StartCombat("rat"))
    response = game.handle_action(Flee())
    assert response.screen is Screens.EXPLORATION
    assert message_keys(response) == ["ui.combat.fled"]
    assert game.combat is None


def win_against_rat(game):
    game.handle_action(StartCombat("rat"))
    for _ in range(3):                                    # 5 + 5 + 5 >= 12
        response = game.handle_action(AttackEnemy())
    return response


def test_victory_records_the_encounter(game):
    response = win_against_rat(game)
    assert game.world_state.defeated == {EncounterRef(DEN, "rat")}
    assert "rat" not in [e.id for e in response.view.encounters]


def test_defeated_encounter_cannot_be_fought_again(game):
    win_against_rat(game)
    game.player.health = game.player.max_health
    response = game.handle_action(StartCombat("rat"))
    assert response.screen is Screens.EXPLORATION
    assert game.combat is None


def test_respawning_encounter_is_never_recorded(game):
    game.handle_action(StartCombat("nest"))
    for _ in range(3):
        response = game.handle_action(AttackEnemy())
    assert response.screen is Screens.EXPLORATION
    assert game.world_state.defeated == set()
    assert "nest" in [e.id for e in response.view.encounters]


def test_victory_grants_xp(game):
    response = win_against_rat(game)
    assert game.player.xp == 8
    assert response.messages[1] == Message(key="ui.combat.xp_gained", params={"xp": 8})


def test_victory_announces_level_up(game):
    game.player.xp = LEVEL_XP[1] - 1
    response = win_against_rat(game)
    assert game.player.level == 2
    assert message_keys(response) == ["ui.combat.victory", "ui.combat.xp_gained", "ui.combat.level_up"]


def test_fleeing_grants_no_xp(game):
    game.handle_action(StartCombat("rat"))
    game.handle_action(Flee())
    assert game.player.xp == 0


@pytest.mark.parametrize("player_level, expected", [(1, 10), (2, 10), (3, 7), (4, 4), (6, 1), (20, 1)])
def test_xp_drops_once_the_player_outlevels_the_enemy(player_level, expected):
    assert xp_gain(10, 2, player_level) == expected


def test_xp_free_enemy_gives_nothing():
    assert xp_gain(0, 1, 1) == 0


def test_combat_xp_adds_up_every_foe():
    combat = CombatState.start(fighter(), [enemy("rat", 12, 3, xp=5), enemy("bat", 5, 1, xp=4, level=3)])
    assert combat.xp_reward(player_level=2) == 4 + 4          # rat dépassé d'un niveau : 5 × 0.7 ≈ 4 ; chauve-souris pleine


def test_fleeing_does_not_record_the_encounter(game):
    game.handle_action(StartCombat("rat"))
    response = game.handle_action(Flee())
    assert game.world_state.defeated == set()
    assert "rat" in [e.id for e in response.view.encounters]


def test_defeat_leads_to_game_over_then_main_menu(game):
    game.handle_action(StartCombat("ogre"))
    response = game.handle_action(AttackEnemy())
    assert response.screen is Screens.GAME_OVER
    assert message_keys(response) == ["ui.combat.defeat"]
    assert game.player.health == 0

    response = game.handle_action(Quit())
    assert response.screen is Screens.MAIN_MENU
    assert game.player is None


def test_faster_enemy_strikes_first(game):
    game.handle_action(StartCombat("wolf"))
    log = game.handle_action(AttackEnemy()).view.log
    assert [e.attacker for e in log] == ["enemy", "player"]


def test_crit_is_logged(game):
    game.rng = FixedRolls(0.0)                       # premier jet : crit
    game.catalog = ItemCatalog({"club": Item(id="club", category="weapons", slots=((Slot.RIGHT_HAND,),),
                                             attack=Attack(crit_chance=0.5, crit_multiplier=2.0))})
    game.player.inventory.equipped.append(Equipped(slots=(Slot.RIGHT_HAND,), instance=ItemInstance("club", wear=1.0)))
    game.handle_action(StartCombat("rat"))
    assert game.handle_action(AttackEnemy()).view.log[0] == CombatLogEntry("player", 10, crit=True)


def test_worn_out_weapon_never_crits(game):
    game.rng = FixedRolls(0.0)
    game.catalog = ItemCatalog({"club": Item(id="club", category="weapons", slots=((Slot.RIGHT_HAND,),),
                                             attack=Attack(crit_chance=0.5, crit_multiplier=2.0))})
    game.player.inventory.equipped.append(Equipped(slots=(Slot.RIGHT_HAND,), instance=ItemInstance("club", wear=0.0)))
    game.handle_action(StartCombat("rat"))
    assert game.handle_action(AttackEnemy()).view.log[0] == CombatLogEntry("player", 5, crit=False)
