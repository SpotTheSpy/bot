from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import LazyProxy, I18nContext
from aiogram_i18n.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from src.bot.actions.back import BackAction
from src.bot.actions.impostor_game.play import ImpostorGamePlayAction
from src.bot.actions.impostor_game.setup import (
    ImpostorGameSetupAction,
    ImpostorGameSetupPlayerAmountAction,
    ImpostorGameSetupImpostorCountAction,
)
from src.core.enums.impostor_count import ImpostorCount
from src.core.enums.impostor_game_parameter import ImpostorGameParameter


def impostor_game_setup_keyboard(
        i18n: I18nContext,
        player_count: int,
        impostor_count: ImpostorCount,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LazyProxy(
                        "setup-impostor-game.button-player-count",
                        player_count=player_count,
                    ),
                    callback_data=ImpostorGameSetupAction(game_parameter=ImpostorGameParameter.PLAYER_COUNT).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=LazyProxy(
                        "setup-impostor-game.button-impostor-count",
                        impostor_count=i18n.get("parameters-impostor-count", impostor_count=impostor_count),
                    ),
                    callback_data=ImpostorGameSetupAction(game_parameter=ImpostorGameParameter.IMPOSTOR_COUNT).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=LazyProxy("button-back"),
                    callback_data=BackAction().pack(),
                ),
                InlineKeyboardButton(
                    text=LazyProxy("setup-impostor-game.button-play"),
                    callback_data=ImpostorGamePlayAction().pack(),
                ),
            ],
        ]
    )


def impostor_game_setup_player_count_keyboard(
        selected_player_count: int,
) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for player_count in range(config.game_parameters.MIN_PLAYER_COUNT, config.game_parameters.MAX_PLAYER_COUNT + 1):
        builder.add(
            InlineKeyboardButton(
                text=LazyProxy(
                    "setup-impostor-game-player-count.button",
                    player_count=player_count,
                    selected=str(player_count == selected_player_count).lower(),
                ),
                callback_data=ImpostorGameSetupPlayerAmountAction(player_count=player_count).pack(),
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


def impostor_game_setup_impostor_count_keyboard(
        i18n: I18nContext,
        selected_impostor_count: ImpostorCount,
) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for impostor_count in ImpostorCount:
        impostor_count = ImpostorCount(impostor_count)

        builder.add(
            InlineKeyboardButton(
                text=LazyProxy(
                    "setup-impostor-game-impostor-count.button",
                    impostor_count=i18n.get("parameters-impostor-count", impostor_count=impostor_count),
                    selected=str(impostor_count == selected_impostor_count).lower(),
                ),
                callback_data=ImpostorGameSetupImpostorCountAction(impostor_count=impostor_count).pack(),
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
