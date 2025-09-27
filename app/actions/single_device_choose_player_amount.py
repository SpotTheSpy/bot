from app.actions.action import Action


class SingleDeviceChoosePlayerAmountAction(Action, prefix="single_device_choose_player_amount"):
    player_amount: int
