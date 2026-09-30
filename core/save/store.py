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
    
    def list_slots_info(self) -> list[dict[str, int | str | None]]:
        return storage.slots_info()

    def delete(self, slot: int) -> None:
        storage.delete(slot)