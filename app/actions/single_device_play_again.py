from app.actions.action import Action


class SingleDevicePlayAgainAction(Action, prefix="single_device_play_again"):
    """
    Callback action for restarting a single-device game.
    """
