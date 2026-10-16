from core.enemies.base import Enemy


class UnknownEnemy(KeyError):
    pass


class EnemyCatalog:
    """Définitions statiques des ennemis, indexées par id."""

    def __init__(self, enemies: dict[str, Enemy] | None = None):
        self._enemies: dict[str, Enemy] = dict(enemies or {})

    def __contains__(self, enemy_id: str) -> bool:
        return enemy_id in self._enemies

    def __len__(self) -> int:
        return len(self._enemies)

    def get(self, enemy_id: str) -> Enemy:
        try:
            return self._enemies[enemy_id]
        except KeyError:
            raise UnknownEnemy(enemy_id) from None
