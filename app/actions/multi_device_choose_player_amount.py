from app.actions.action import Action


class MultiDeviceChoosePlayerAmountAction(Action, prefix="multi_device_choose_player_amount"):
    player_amount: int
