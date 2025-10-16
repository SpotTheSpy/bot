from app.actions.action import Action


class MultiDeviceLeaveAction(Action, prefix="multi_device_leave"):
    """
    Callback action for leaving a multi-device game.
    """
