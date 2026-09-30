from dataclasses import dataclass
from core.enums import Stat
from core.world.models import RoomRef, WorldState
from core.game.response import Message
import core.save.codec as codec
from core.game.snapshot import GameSnapshot

class SaveStore:
    def save(self, slot: int, snapshot: GameSnapshot):
        pass

    def list_slots(self) -> list[int]:
        pass