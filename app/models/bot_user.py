from functools import wraps
from inspect import FullArgSpec, getfullargspec
from typing import Dict, Any, List, Self, ClassVar, Optional, TYPE_CHECKING, Callable
from uuid import UUID

from aiogram import Bot
from aiogram.exceptions import AiogramError
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    InputFile,
    MessageEntity,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    CallbackQuery,
    TelegramObject
)
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import gettext as _
from babel.support import LazyProxy

from app.controllers.redis import RedisController
from app.enums.language_type import LanguageType
from app.enums.player_role import PlayerRole
from app.exceptions.already_in_game import AlreadyInGameError
from app.models.qr_code import QRCode
from app.models.redis import AbstractRedisModel
from app.models.single_device_game import SingleDeviceGame
from app.models.user import User
from app.parameters import Parameters
from app.utils.dict_factory import DictFactory
from app.utils.inline_keyboard_factory import InlineKeyboardFactory
from app.utils.logging import logger
from app.utils.secret_words import SecretWordsController
from config import Config

if TYPE_CHECKING:
    from app.controllers.multi_device_games import MultiDeviceGamesController
    from app.controllers.users import UsersController
    from app.controllers.single_device_games import SingleDeviceGamesController
else:
    MultiDeviceGamesController = Any
    UsersController = Any
    SingleDeviceGamesController = Any


def _with_workflow_data(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        spec: FullArgSpec = getfullargspec(func)

        if len(spec.args) > 1:
            if isinstance(self._event, spec.annotations[spec.args[1]]):
                args = (self._event,) + args

        kwargs.update(self._workflow_data)

        if not spec.varkw:
            kwargs = {
                key: argument for key, argument in kwargs.items()
                if key in spec.args or key in spec.kwonlyargs
            }

        return await func(self, *args, **kwargs)

    return wrapper


class BotUser(User, AbstractRedisModel, arbitrary_types_allowed=True):
    key: ClassVar[str] = "bot_user"

    chat_id: int | None = None
    message_id: int | None = None
    has_photo: bool | None = None

    _bot: Bot | None = None
    _state: FSMContext | None = None
    _config: Config | None = None
    _i18n: I18n | None = None
    _users: Optional['UsersController'] = None
    _single_device_games: Optional['SingleDeviceGamesController'] = None
    _multi_device_games: Optional['MultiDeviceGamesController'] = None
    _qr_codes: Optional[RedisController[QRCode]] = None

    _event: TelegramObject | None = None
    _workflow_data: Dict[str, Any] | None = None

    @property
    def bot(self) -> Bot:
        if self._bot is None:
            raise ValueError("Bot is not set")
        return self._bot

    @property
    def state(self) -> FSMContext:
        if self._state is None:
            raise ValueError("State is not set")
        return self._state

    @property
    def config(self) -> Config:
        if self._config is None:
            raise ValueError("Config is not set")
        return self._config

    @property
    def i18n(self) -> I18n:
        if self._i18n is None:
            raise ValueError("I18n is not set")
        return self._i18n

    @property
    def users(self) -> 'UsersController':
        if self._users is None:
            raise ValueError("Users is not set")
        return self._users

    @property
    def single_device_games(self) -> Optional['SingleDeviceGamesController']:
        if self._single_device_games is None:
            raise ValueError("SingleDeviceGames is not set")
        return self._single_device_games

    @property
    def multi_device_games(self) -> Optional['MultiDeviceGamesController']:
        if self._multi_device_games is None:
            raise ValueError("MultiDeviceGames is not set")
        return self._multi_device_games

    @property
    def qr_codes(self) -> Optional[RedisController[QRCode]]:
        if self._qr_codes is None:
            raise ValueError("QRCode is not set")
        return self._qr_codes

    @classmethod
    def from_workflow_data(
            cls,
            data: Dict[str, Any] | None,
            *,
            controller: RedisController[Self],
            event: TelegramObject | None = None,
            workflow_data: Dict[str, Any] | None = None,
            **kwargs: Any
    ) -> Self | None:
        user = cls.from_json(data, **kwargs)

        if user is not None:
            user._controller = controller
            user._bot = workflow_data.get("bot")
            user._config = workflow_data.get("config")
            user._i18n = workflow_data.get("i18n")
            user._users = workflow_data.get("users")
            user._single_device_games = workflow_data.get("single_device_games")
            user._multi_device_games = workflow_data.get("multi_device_games")
            user._qr_codes = workflow_data.get("qr_codes")

            user._event = event
            user._workflow_data = workflow_data

        return user

    async def new_message(
            self,
            chat_id: int,
            text: str | LazyProxy | None = None,
            photo: str | InputFile | None = None,
            entities: List[MessageEntity] | None = None,
            reply_markup: InlineKeyboardMarkup | None = None
    ) -> Message | None:
        if chat_id is not None:
            self.chat_id = chat_id

        params: Dict[str, Any] = {
            "entities": entities,
            "reply_markup": reply_markup
        }

        if entities:
            params["parse_mode"] = None

        try:
            with self.i18n.use_locale(self.locale):
                if photo is None:
                    new_message: Message = await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=text,
                        **params
                    )
                    if self.message_id is not None:
                        await self.bot.delete_message(
                            self.chat_id,
                            self.message_id
                        )
                else:
                    params["caption_entities"] = params.pop("entities")

                    new_message: Message = await self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=photo,
                        caption=text,
                        **params
                    )
                    if self.message_id is not None:
                        await self.bot.delete_message(
                            self.chat_id,
                            self.message_id
                        )
        except AiogramError:
            return

        self.chat_id = new_message.chat.id
        self.message_id = new_message.message_id
        self.has_photo = new_message.photo is not None

        await self.save()
        return new_message

    async def edit_message(
            self,
            chat_id: int | None = None,
            message_id: int | None = None,
            text: str | LazyProxy | None = None,
            photo: str | InputFile | None = None,
            entities: List[MessageEntity] | None = None,
            reply_markup: InlineKeyboardMarkup | None = None,
            only_edit_caption: bool = False
    ) -> Message | None:
        if chat_id is not None:
            self.chat_id = chat_id
        elif self.chat_id is None:
            return

        if message_id is not None:
            self.message_id = message_id
        elif self.message_id is None:
            return

        params: Dict[str, Any] = {
            "entities": entities,
            "reply_markup": reply_markup
        }

        if entities:
            params["parse_mode"] = None

        try:
            with self.i18n.use_locale(self.locale):
                if photo is None:
                    if only_edit_caption:
                        if self.has_photo:
                            params["caption_entities"] = params.pop("entities")

                            new_message: Message = await self.bot.edit_message_caption(
                                chat_id=self.chat_id,
                                message_id=self.message_id,
                                caption=text,
                                **params
                            )
                        else:
                            return
                    else:
                        if not self.has_photo:
                            new_message: Message = await self.bot.edit_message_text(
                                chat_id=self.chat_id,
                                message_id=self.message_id,
                                text=text,
                                **params
                            )
                        else:
                            new_message: Message = await self.bot.send_message(
                                chat_id=self.chat_id,
                                text=text,
                                **params
                            )
                            await self.bot.delete_message(
                                self.chat_id,
                                self.message_id
                            )
                else:
                    if self.has_photo:
                        params["caption_entities"] = params.pop("entities")
                        params.pop("reply_markup")

                        new_message: Message = await self.bot.edit_message_media(
                            chat_id=self.chat_id,
                            message_id=self.message_id,
                            media=InputMediaPhoto(
                                media=photo,
                                caption=text,
                                **params
                            ),
                            reply_markup=reply_markup
                        )
                    else:
                        params["caption_entities"] = params.pop("entities")

                        new_message: Message = await self.bot.send_photo(
                            chat_id=self.chat_id,
                            photo=photo,
                            caption=text,
                            **params
                        )
                        await self.bot.delete_message(
                            self.chat_id,
                            self.message_id
                        )
        except AiogramError as e:
            logger.exception(e)
            return

        self.chat_id = new_message.chat.id
        self.message_id = new_message.message_id
        self.has_photo = new_message.photo is not None

        await self.save()
        return new_message

    async def save(self) -> None:
        await self.controller.set(self)

    @_with_workflow_data
    async def new_start_message(
            self,
            start_command_message: Message,
            *,
            locale: str | None = None
    ) -> None:
        await self.new_message(
            start_command_message.chat.id,
            text=_("message.start", locale=locale),
            reply_markup=InlineKeyboardFactory.start_keyboard(locale=locale)
        )
        await start_command_message.delete()

    @_with_workflow_data
    async def start_message(
            self,
            callback_query: CallbackQuery,
            *,
            locale: str | None = None
    ) -> None:
        await self.edit_message(
            text=_("message.start", locale=locale),
            reply_markup=InlineKeyboardFactory.start_keyboard(locale=locale)
        )
        await callback_query.answer()

    @_with_workflow_data
    async def language_message(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.edit_message(
            text=_("message.language.choose"),
            reply_markup=InlineKeyboardFactory.choose_language_keyboard()
        )
        await callback_query.answer()

    @_with_workflow_data
    async def choose_language(
            self,
            callback_query: CallbackQuery,
            *,
            new_language: LanguageType
    ) -> None:
        if self.locale == new_language:
            await callback_query.answer(_("answer.language.same"))
            return

        await self.users.update_user(
            self.id,
            locale=new_language
        )

        self.locale = new_language
        await self.save()

    @_with_workflow_data
    async def choose_device_message(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.edit_message(
            text=_("message.choose_device"),
            reply_markup=InlineKeyboardFactory.choose_device_keyboard()
        )
        await callback_query.answer()

    @_with_workflow_data
    async def explain_single_device(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.edit_message(
            text=_("message.single_device.explain"),
            reply_markup=InlineKeyboardFactory.single_device_explain_keyboard()
        )
        await callback_query.answer()

    @_with_workflow_data
    async def configure_single_device(
            self,
            callback_query: CallbackQuery,
            *,
            state: FSMContext,
            player_amount: int | None = None
    ) -> None:
        if player_amount is None:
            player_amount: int = Parameters.DEFAULT_PLAYER_AMOUNT

        await state.update_data(player_amount=player_amount)

        await self.edit_message(
            text=_("message.single_device.configure"),
            reply_markup=InlineKeyboardFactory.single_device_configure_keyboard(
                min_amount=Parameters.MIN_PLAYER_AMOUNT,
                max_amount=Parameters.MAX_PLAYER_AMOUNT,
                selected_amount=player_amount
            )
        )
        await callback_query.answer()

    @_with_workflow_data
    async def create_single_device_game(
            self,
            *,
            state: FSMContext,
            single_device_games: 'SingleDeviceGamesController',
            player_amount: int
    ) -> SingleDeviceGame | None:
        try:
            game: SingleDeviceGame = await single_device_games.create_game(
                self.id,
                self.telegram_id,
                player_amount
            )
        except AlreadyInGameError:
            return

        await state.update_data(game=game.to_json())
        return game

    @_with_workflow_data
    async def get_single_device_game(
            self,
            *,
            state: FSMContext,
            single_device_games: 'SingleDeviceGamesController'
    ) -> SingleDeviceGame | None:
        return (
            SingleDeviceGame.from_json(await state.get_value("game"))
            or await single_device_games.get_game_by_user_id(self.id)
        )

    @_with_workflow_data
    async def end_single_device_game(
            self,
            *,
            single_device_games: 'SingleDeviceGamesController',
            game_id: UUID | None = None
    ) -> None:
        if game_id is None:
            game_id: UUID = (await single_device_games.get_game_by_user_id(self.id)).game_id

        if game_id is None:
            return

        await single_device_games.remove_game(game_id)

    @_with_workflow_data
    async def start_single_device_game(
            self,
            callback_query: CallbackQuery,
            *,
            state: FSMContext,
            player_amount: int
    ) -> None:
        game: SingleDeviceGame | None = await self.create_single_device_game(player_amount=player_amount)

        if game is None:
            return  # TODO: Error message

        player_index: int = 0
        await state.update_data(player_index=player_index)

        await callback_query.answer()
        await self._prepare_in_single_device_game(player_index, game.player_amount)

        logger.info(
            f"{self.first_name} (id={self.id}) "
            f"started a single-device game"
        )

    @_with_workflow_data
    async def view_role_in_single_device_game(
            self,
            callback_query: CallbackQuery,
            *,
            state: FSMContext
    ) -> None:
        game: SingleDeviceGame | None = await self.get_single_device_game()

        if game is None:
            return  # TODO: Error message

        player_index: int = await state.get_value("player_index")
        role: PlayerRole = PlayerRole.SPY if player_index == game.spy_index else PlayerRole.CITIZEN

        await self.edit_message(
            text=DictFactory.single_device_role_message().get(role).format(
                secret_word=SecretWordsController.get_secret_word(game.secret_word),
                player_index=player_index + 1,
                player_amount=game.player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_proceed_keyboard()
        )
        await callback_query.answer()

    @_with_workflow_data
    async def proceed_in_single_device_game(
            self,
            callback_query: CallbackQuery,
            *,
            state: FSMContext
    ) -> None:
        game: SingleDeviceGame | None = await self.get_single_device_game()

        if game is None:
            return  # TODO: Error message

        player_index: int | None = await state.get_value("player_index") + 1
        await state.update_data(player_index=player_index)

        if player_index < game.player_amount:
            await self._prepare_in_single_device_game(player_index, game.player_amount)
        else:
            await self._discuss_in_single_device_game()

        await callback_query.answer()

    @_with_workflow_data
    async def finish_single_device_game(
            self,
            callback_query: CallbackQuery
    ) -> None:
        game: SingleDeviceGame | None = await self.get_single_device_game()

        if game is None:
            return  # TODO: Error message

        await self.edit_message(
            text=_("message.single_device.play.finish").format(
                secret_word=SecretWordsController.get_secret_word(game.secret_word),
                spy_index=game.spy_index + 1
            ),
            reply_markup=InlineKeyboardFactory.single_device_play_again_keyboard()
        )
        await callback_query.answer()

        logger.info(
            f"{self.first_name} (id={self.id}) "
            f"finished a single-device game (game_id={game.game_id})"
        )

    @_with_workflow_data
    async def restart_single_device_game(self) -> None:
        game: SingleDeviceGame = await self.get_single_device_game()

        if game is None:
            return  # TODO: Error message

        await self.end_single_device_game(game_id=game.game_id)
        await self.start_single_device_game(player_amount=game.player_amount)

    async def _prepare_in_single_device_game(
            self,
            player_index: int,
            player_amount: int
    ) -> None:
        await self.edit_message(
            text=_("message.single_device.play.prepare").format(
                player_index=player_index + 1,
                player_amount=player_amount
            ),
            reply_markup=InlineKeyboardFactory.single_device_view_role_keyboard()
        )

    async def _discuss_in_single_device_game(self) -> None:
        await self.edit_message(
            text=_("message.single_device.play.discuss"),
            reply_markup=InlineKeyboardFactory.single_device_finish_keyboard()
        )
