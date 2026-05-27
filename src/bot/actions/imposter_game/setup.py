from src.bot.actions.base import BaseAction
from src.core.enums.imposter_count import ImposterCount
from src.core.enums.imposter_game_parameter import ImposterGameParameter


class ImposterGameSetupAction(BaseAction, prefix="imposter_game_setup"):
    """
    Callback action for configuring an imposter game parameter.
    """

    game_parameter: ImposterGameParameter
    """
    Desired game parameter.
    """


class ImposterGameSetupPlayerAmountAction(BaseAction, prefix="imposter_game_setup_player_count"):
    """
    Callback action for choosing player count in an imposter game.
    """

    player_count: int
    """
    New player amount to be set.
    """


class ImposterGameSetupImposterCountAction(BaseAction, prefix="imposter_game_setup_imposter_count"):
    """
    Callback action for configuring an imposter game secret word category.
    """

    imposter_count: ImposterCount
    """
    New imposter count to be set.
    """
