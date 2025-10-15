from app.actions.action import Action


class SwitchSceneAction(Action, prefix="switch"):
    """
    Callback action for switching to a new scene.
    """

    scene: str
