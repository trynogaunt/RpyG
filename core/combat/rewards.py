"""Ce que rapporte une victoire."""
from core.game.rules import XP_FALLOFF_FLOOR, XP_FALLOFF_PER_LEVEL


def xp_gain(base: int, enemy_level: int, player_level: int) -> int:
    """XP d'un ennemi vaincu : pleine tant que le joueur ne le dépasse pas, puis de moins en moins.

    Au moins 1 dès que l'ennemi rapporte quelque chose.
    """
    if not base:
        return 0
    gap = max(0, player_level - enemy_level)
    ratio = max(XP_FALLOFF_FLOOR, 1 - XP_FALLOFF_PER_LEVEL * gap)
    return max(1, round(base * ratio))
