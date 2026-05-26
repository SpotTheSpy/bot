from src.bot.actions.base import BaseAction
from src.core.enums.spy_category import SpyCategory
from src.core.enums.spy_count import SpyCount
from src.core.enums.spy_game_parameter import SpyGameParameter


class SpyGameSetupAction(BaseAction, prefix="spy_game_setup"):
    """
    Callback action for configuring a spy game parameter.
    """

    game_parameter: SpyGameParameter
    """
    Desired game parameter.
    """


class SpyGameSetupPlayerAmountAction(BaseAction, prefix="spy_game_setup_player_count"):
    """
    Callback action for choosing player count in a spy game.
    """

    player_count: int
    """
    New player amount to be set.
    """


class SpyGameSetupCategoryAction(BaseAction, prefix="spy_game_setup_category"):
    """
    Callback action for configuring a spy game secret word category.
    """

    category: SpyCategory
    """
    New category to be set.
    """


class SpyGameSetupSpyCountAction(BaseAction, prefix="spy_game_setup_spy_count"):
    """
    Callback action for configuring a spy game secret word category.
    """

    spy_count: SpyCount
    """
    New spy count to be set.
    """
