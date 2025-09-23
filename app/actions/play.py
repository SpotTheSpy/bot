from app.actions.action import Action
from app.enums.game_style import GameStyle


class PlayAction(Action, prefix="play"):
    style: GameStyle
