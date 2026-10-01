"""Fixtures partagées par tous les fichiers de tests.

pytest charge ce fichier automatiquement : les fixtures définies ici sont
utilisables dans n'importe quel test, sans import.
"""
import pytest

from core.enums import Direction
from core.game.actions import NewGame
from core.game.game import Game
from core.world.models import Room, RoomRef, World, Zone


@pytest.fixture
def small_world() -> World:
    """Deux zones reliées.

    village :  square --S--> gate --S--> [cave]
                      <--N--      <--N--
    cave    :  entrance --S--> pool
                        <--N--
    """
    square = RoomRef("village", "square")
    gate = RoomRef("village", "gate")
    entrance = RoomRef("cave", "entrance")
    pool = RoomRef("cave", "pool")

    village = Zone(
        id="village",
        name="Village",
        description="Un petit village.",
        entry_room="square",
        rooms={
            "square": Room("Place", "La place du village.", square,
                           look_around="Des enfants jouent.",
                           exits={Direction.SOUTH: gate}),
            "gate": Room("Porte", "La porte du village.", gate,
                         exits={Direction.NORTH: square, Direction.SOUTH: entrance}),
        },
    )
    cave = Zone(
        id="cave",
        name="Grotte",
        description="Une grotte humide.",
        entry_room="entrance",
        rooms={
            "entrance": Room("Entrée", "L'entrée de la grotte.", entrance,
                             exits={Direction.NORTH: gate, Direction.SOUTH: pool}),
            "pool": Room("Bassin", "Un bassin d'eau froide.", pool,
                         exits={Direction.NORTH: entrance}),
        },
    )
    return World(start=square, zones={"village": village, "cave": cave})


@pytest.fixture
def game(small_world) -> Game:
    """Un jeu démarré, sur le menu principal."""
    g = Game(world=small_world)
    g.start()
    return g


@pytest.fixture
def game_in_creation(game) -> Game:
    """Un jeu sur l'écran de création, formulaire vierge."""
    game.handle_action(NewGame())
    return game