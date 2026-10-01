from core.errors import InvalidSave
from core.game.snapshot import GameSnapshot
from core.save import codec, storage
from core.views.slot_view import SlotView
from core.save.storage import MAX_SLOTS


class SaveStore:
    def save(self, slot: int, snapshot: GameSnapshot) -> None:
        storage.write(slot, codec.encode(snapshot))

    def load(self, slot: int) -> GameSnapshot:
        return codec.decode(storage.read(slot))   # lève InvalidSave

    def list_slots(self) -> list[int]:
        return storage.slots()
    
    def list_slots_info(self) -> tuple[SlotView, ...]:
        infos = []
        for slot in range(1, MAX_SLOTS + 1):
            if slot not in storage.slots():
                infos.append(SlotView(slot=slot, name=None, level=None,
                                    location=None, saved_at=None))
                continue
            try:
                data = storage.read(slot)
                meta = data["meta"]
                infos.append(SlotView(
                    slot=slot,
                    name=meta["name"],
                    level=meta["level"],
                    location=meta["location"],
                    saved_at=data["saved_at"],
                ))
            except (InvalidSave, KeyError, TypeError):
                infos.append(SlotView(slot=slot, name=None, level=None,
                                    location=None, saved_at=None, readable=False))
        return tuple(infos)

    def delete(self, slot: int) -> None:
        storage.delete(slot)