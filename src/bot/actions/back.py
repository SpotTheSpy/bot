from src.bot.actions.base import BaseAction


class BackAction(BaseAction, prefix="back"):
    """
    Callback action for returning to the previous scene.
    """
