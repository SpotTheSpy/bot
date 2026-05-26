from src.bot.actions.base import BaseAction
from src.core.enums.spy_category import SpyCategory
from src.core.enums.spy_count import SpyCount
from src.core.enums.spy_game_parameter import SpyGameParameter


class SpySetupAction(BaseAction, prefix="spy_setup"):
    """
    Callback action for configuring a spy game parameter.
    """

    game_parameter: SpyGameParameter
    """
    Desired game parameter.
    """


class SpySetupPlayerAmountAction(BaseAction, prefix="spy_setup_player_count"):
    """
    Callback action for choosing player count in a spy game.
    """

    player_count: int
    """
    New player amount to be set.
    """


class SpySetupCategoryAction(BaseAction, prefix="spy_setup_category"):
    """
    Callback action for configuring a spy game secret word category.
    """

    category: SpyCategory
    """
    New category to be set.
    """


class SpySetupSpyCountAction(BaseAction, prefix="spy_setup_spy_count"):
    """
    Callback action for configuring a spy game secret word category.
    """

    spy_count: SpyCount
    """
    New spy count to be set.
    """
