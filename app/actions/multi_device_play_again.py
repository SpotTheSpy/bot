from app.actions.action import Action


class MultiDevicePlayAgainAction(Action, prefix="multi_device_play_again"):
    """
    Callback action for restarting a multi-device game.
    """
