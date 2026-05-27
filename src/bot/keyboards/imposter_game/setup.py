from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import LazyProxy, I18nContext
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from src.bot.actions.back import BackAction
from src.bot.actions.imposter_game.play import ImposterGamePlayAction
from src.bot.actions.imposter_game.setup import (
    ImposterGameSetupAction,
    ImposterGameSetupPlayerAmountAction,
    ImposterGameSetupImposterCountAction,
)
from src.core.enums.imposter_count import ImposterCount
from src.core.enums.imposter_game_parameter import ImposterGameParameter


def imposter_game_setup_keyboard(
        i18n: I18nContext,
        player_count: int,
        imposter_count: ImposterCount,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LazyProxy(
                        "setup-imposter-game.button-player-count",
                        player_count=player_count,
                    ),
                    callback_data=ImposterGameSetupAction(game_parameter=ImposterGameParameter.PLAYER_COUNT).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=LazyProxy(
                        "setup-imposter-game.button-imposter-count",
                        imposter_count=i18n.get("parameters-imposter-count", imposter_count=imposter_count),
                    ),
                    callback_data=ImposterGameSetupAction(game_parameter=ImposterGameParameter.IMPOSTER_COUNT).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=LazyProxy("button-back"),
                    callback_data=BackAction().pack(),
                ),
                InlineKeyboardButton(
                    text=LazyProxy("setup-imposter-game.button-play"),
                    callback_data=ImposterGamePlayAction().pack(),
                ),
            ],
        ]
    )


def imposter_game_setup_player_count_keyboard(
        selected_player_count: int,
) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for player_count in range(config.game_parameters.MIN_PLAYER_COUNT, config.game_parameters.MAX_PLAYER_COUNT + 1):
        builder.add(
            InlineKeyboardButton(
                text=LazyProxy(
                    "setup-imposter-game-player-count.button",
                    player_count=player_count,
                    selected=str(player_count == selected_player_count).lower(),
                ),
                callback_data=ImposterGameSetupPlayerAmountAction(player_count=player_count).pack(),
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


def imposter_game_setup_imposter_count_keyboard(
        i18n: I18nContext,
        selected_imposter_count: ImposterCount,
) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for imposter_count in ImposterCount:
        imposter_count = ImposterCount(imposter_count)

        builder.add(
            InlineKeyboardButton(
                text=LazyProxy(
                    "setup-imposter-game-imposter-count.button",
                    imposter_count=i18n.get("parameters-imposter-count", imposter_count=imposter_count),
                    selected=str(imposter_count == selected_imposter_count).lower(),
                ),
                callback_data=ImposterGameSetupImposterCountAction(imposter_count=imposter_count).pack(),
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
