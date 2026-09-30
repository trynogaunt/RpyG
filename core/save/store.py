from core.errors import InvalidSave
from core.game.snapshot import GameSnapshot
from core.save import codec, storage


class SaveStore:
    def save(self, slot: int, snapshot: GameSnapshot) -> None:
        storage.write(slot, codec.encode(snapshot))

    def load(self, slot: int) -> GameSnapshot:
        return codec.decode(storage.read(slot))   # lève InvalidSave

    def list_slots(self) -> list[int]:
        return storage.slots()