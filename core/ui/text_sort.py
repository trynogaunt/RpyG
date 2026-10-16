import unicodedata


def sort_key(text: str) -> str:
    """Clé de tri alphabétique sans casse ni accents (« Épée » rangée avec les « e »)."""
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return "".join(c for c in decomposed if not unicodedata.combining(c))
