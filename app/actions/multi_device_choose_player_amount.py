from app.actions.action import Action


class MultiDeviceChoosePlayerAmountAction(Action, prefix="multi_device_choose_player_amount"):
    """
    Callback action for choosing player count in a multi-device game.
    """

    player_amount: int
