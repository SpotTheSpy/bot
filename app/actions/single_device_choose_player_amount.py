from app.actions.action import Action


class SingleDeviceChoosePlayerAmountAction(Action, prefix="single_device_choose_player_amount"):
    """
    Callback action for choosing player count in a single-device game.

    Attributes:
        player_amount: New player amount to be set.
    """

    player_amount: int
    """
    New player amount to be set.
    """
