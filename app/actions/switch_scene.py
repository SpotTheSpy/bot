from app.actions.action import Action


class SwitchSceneAction(Action, prefix="switch"):
    """
    Callback action for switching to a new scene.

    Attributes:
        scene: Scene to switch.
    """

    scene: str
    """
    Scene to switch to.
    """
