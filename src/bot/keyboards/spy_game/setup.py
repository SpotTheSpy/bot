from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import LazyProxy, I18nContext
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from src.bot.actions.back import BackAction
from src.bot.actions.spy_game.play import SpyGamePlayAction
from src.bot.actions.spy_game.setup import (
    SpyGameSetupAction,
    SpyGameSetupPlayerAmountAction,
    SpyGameSetupCategoryAction,
    SpyGameSetupSpyCountAction,
)
from src.core.enums.spy_category import SpyCategory
from src.core.enums.spy_count import SpyCount
from src.core.enums.spy_game_parameter import SpyGameParameter


def spy_game_setup_keyboard(
        i18n: I18nContext,
        player_count: int,
        category: SpyCategory,
        spy_count: SpyCount,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LazyProxy(
                        "setup-spy-game.button-player-count",
                        player_count=player_count,
                    ),
                    callback_data=SpyGameSetupAction(game_parameter=SpyGameParameter.PLAYER_COUNT).pack(),
                ),
                InlineKeyboardButton(
                    text=LazyProxy(
                        "setup-spy-game.button-category",
                        category=i18n.get("parameters-spy-categories", category=category),
                    ),
                    callback_data=SpyGameSetupAction(game_parameter=SpyGameParameter.CATEGORY).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=LazyProxy(
                        "setup-spy-game.button-spy-count",
                        spy_count=i18n.get("parameters-spy-count", spy_count=spy_count),
                    ),
                    callback_data=SpyGameSetupAction(game_parameter=SpyGameParameter.SPY_COUNT).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=LazyProxy("button-back"),
                    callback_data=BackAction().pack(),
                ),
                InlineKeyboardButton(
                    text=LazyProxy("setup-spy-game.button-play"),
                    callback_data=SpyGamePlayAction().pack(),
                ),
            ],
        ]
    )


def spy_game_setup_player_count_keyboard(
        selected_player_count: int,
) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for player_count in range(config.game_parameters.MIN_PLAYER_COUNT, config.game_parameters.MAX_PLAYER_COUNT + 1):
        builder.add(
            InlineKeyboardButton(
                text=LazyProxy(
                    "setup-spy-game-player-count.button",
                    player_count=player_count,
                    selected=str(player_count == selected_player_count).lower(),
                ),
                callback_data=SpyGameSetupPlayerAmountAction(player_count=player_count).pack(),
            )
        )

    builder.add(
        InlineKeyboardButton(
            text=LazyProxy("button-back"),
            callback_data=BackAction().pack(),
        )
    )

    builder.adjust(3, 3, 1)
    return builder.as_markup()


def spy_game_setup_category_keyboard(
        i18n: I18nContext,
        selected_category: SpyCategory,
) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for category in SpyCategory:
        category = SpyCategory(category)

        builder.add(
            InlineKeyboardButton(
                text=LazyProxy(
                    "setup-spy-game-category.button",
                    category=i18n.get("parameters-spy-categories", category=category),
                    selected=str(category == selected_category).lower(),
                ),
                callback_data=SpyGameSetupCategoryAction(category=category).pack(),
            )
        )

    builder.add(
        InlineKeyboardButton(
            text=LazyProxy("button-back"),
            callback_data=BackAction().pack(),
        )
    )

    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()


def spy_game_setup_spy_count_keyboard(
        i18n: I18nContext,
        selected_spy_count: SpyCount,
) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for spy_count in SpyCount:
        spy_count = SpyCount(spy_count)

        builder.add(
            InlineKeyboardButton(
                text=LazyProxy(
                    "setup-spy-game-spy-count.button",
                    spy_count=i18n.get("parameters-spy-count", spy_count=spy_count),
                    selected=str(spy_count == selected_spy_count).lower(),
                ),
                callback_data=SpyGameSetupSpyCountAction(spy_count=spy_count).pack(),
            )
        )

    builder.add(
        InlineKeyboardButton(
            text=LazyProxy("button-back"),
            callback_data=BackAction().pack(),
        )
    )

    builder.adjust(2, 1, 1)
    return builder.as_markup()
