from app.actions.action import Action


class SingleDeviceProceedPlayerAction(Action, prefix="single_device_proceed"):
    """
    Callback action for proceeding to a next player in a single-device game.
    """
