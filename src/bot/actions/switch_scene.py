from src.bot.actions.base import BaseAction


class SwitchSceneAction(BaseAction, prefix="switch"):
    """
    Callback action for proceeding to a new scene.
    """

    scene: str
    """
    Chosen scene state.
    """
