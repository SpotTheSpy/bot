from app.actions.action import Action


class BackAction(Action, prefix="back"):
    """
    Callback action for returning to the previous scene.
    """
