from src.bot.actions.base import BaseAction
from src.core.enums.impostor_count import ImpostorCount
from src.core.enums.impostor_game_parameter import ImpostorGameParameter


class ImpostorGameSetupAction(BaseAction, prefix="impostor_game_setup"):
    """
    Callback action for configuring an impostor game parameter.
    """

    game_parameter: ImpostorGameParameter
    """
    Desired game parameter.
    """


class ImpostorGameSetupPlayerAmountAction(BaseAction, prefix="impostor_game_setup_player_count"):
    """
    Callback action for choosing player count in an impostor game.
    """

    player_count: int
    """
    New player amount to be set.
    """


class ImpostorGameSetupImpostorCountAction(BaseAction, prefix="impostor_game_setup_impostor_count"):
    """
    Callback action for configuring an impostor game secret word category.
    """

    impostor_count: ImpostorCount
    """
    New impostor count to be set.
    """
