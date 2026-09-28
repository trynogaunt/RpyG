from dataclasses import dataclass
from core.enums import Screens
from dataclasses import field
from core.views.base_view import BaseView

@dataclass(frozen=True)
class Message:
    """Represents a message from the game to the player."""
    key: str
    params: dict = field(default_factory=dict)
    fallback_key: str | None = None


@dataclass(frozen=True)
class GameResponse:
    """Represents a response from the game to the player."""
    screen: Screens
    view: BaseView | None = None
    messages: tuple[Message] = ()
    

