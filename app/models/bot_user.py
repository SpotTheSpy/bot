from asyncio import Task, create_task, gather
from functools import wraps
from inspect import FullArgSpec, getfullargspec
from typing import Dict, Any, List, Self, ClassVar, Optional, TYPE_CHECKING, Callable, Tuple, Awaitable
from uuid import UUID

from aiogram import Bot
from aiogram.enums import MessageEntityType
from aiogram.exceptions import AiogramError
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    User as AiogramUser,
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
from app.exceptions.api import APIError
from app.exceptions.game_has_already_started import GameHasAlreadyStartedError
from app.exceptions.invalid_player_amount import InvalidPlayerAmountError
from app.exceptions.not_found import NotFoundError
from app.models.multi_device_game import MultiDeviceGame, MultiDevicePlayer
from app.models.qr_code import QRCode, BlurredQRCode
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
                else:
                    params["caption_entities"] = params.pop("entities")

                    new_message: Message = await self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=photo,
                        caption=text,
                        **params
                    )
        except AiogramError as error:
            logger.warning(
                f"{self.first_name} (id={self.telegram_id}) "
                f"got an error while receiving a new message: {error}"
            )
            return
        else:
            if self.message_id is not None:
                try:
                    await self.bot.delete_message(
                        self.chat_id,
                        self.message_id
                    )
                except AiogramError:
                    pass

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
        except AiogramError as error:
            logger.warning(
                f"{self.first_name} (id={self.telegram_id}) "
                f"got an error while editing message: {error}"
            )
            return
        else:
            try:
                await self.bot.delete_message(
                    self.chat_id,
                    self.message_id
                )
            except AiogramError:
                pass

        self.chat_id = new_message.chat.id
        self.message_id = new_message.message_id
        self.has_photo = new_message.photo is not None

        await self.save()
        return new_message

    async def save(self) -> None:
        await self.controller.set(self)

    @_with_workflow_data
    async def get_bot_user(
            self,
            user_id: UUID
    ) -> Self | None:
        if user_id == self.id:
            return self

        return await self.controller.get(
            user_id,
            workflow_data=self._workflow_data,
            from_json_method=self.from_workflow_data
        )

    @_with_workflow_data
    async def new_start_message(
            self,
            message: Message,
            *,
            locale: str | None = None
    ) -> None:
        await self.new_message(
            message.chat.id,
            text=_("message.start", locale=locale),
            reply_markup=InlineKeyboardFactory.start_keyboard(locale=locale)
        )
        await message.delete()

    @_with_workflow_data
    async def start_message(
            self,
            callback_query: CallbackQuery,
            *,
            new_locale: str | None = None
    ) -> None:
        await self.edit_message(
            text=_("message.start", locale=new_locale),
            reply_markup=InlineKeyboardFactory.start_keyboard(locale=new_locale)
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
    ) -> str | None:
        if self.locale == new_language:
            await callback_query.answer(_("answer.language.same"))
            return

        await self.users.update_user(
            self.id,
            locale=new_language
        )

        self.locale = new_language
        await self.save()

        return new_language

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
            game: SingleDeviceGame = await self.get_single_device_game()

            if game is None:
                return

            game_id = game.game_id

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
            f"{self.first_name} (id={self.telegram_id}) "
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
            f"{self.first_name} (id={self.telegram_id}) "
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

    @_with_workflow_data
    async def explain_multi_device(
            self,
            callback_query: CallbackQuery
    ) -> None:
        await self.edit_message(
            text=_("message.multi_device.explain"),
            reply_markup=InlineKeyboardFactory.multi_device_explain_keyboard()
        )
        await callback_query.answer()

    @_with_workflow_data
    async def configure_multi_device(
            self,
            callback_query: CallbackQuery,
            *,
            state: FSMContext,
            player_amount: int | None = None
    ) -> None:
        if player_amount is None:
            player_amount: int = Parameters.DEFAULT_PLAYER_AMOUNT

        await state.update_data(player_amount=player_amount)

        await callback_query.answer()
        await self.edit_message(
            text=_("message.multi_device.configure"),
            reply_markup=InlineKeyboardFactory.multi_device_configure_keyboard(
                min_amount=Parameters.MIN_PLAYER_AMOUNT,
                max_amount=Parameters.MAX_PLAYER_AMOUNT,
                selected_amount=player_amount
            )
        )
        await callback_query.answer()

    @_with_workflow_data
    async def create_multi_device_game(
            self,
            *,
            multi_device_games: 'MultiDeviceGamesController',
            player_amount: int
    ) -> MultiDeviceGame | None:
        try:
            game: MultiDeviceGame = await multi_device_games.create_game(
                self.id,
                player_amount=player_amount
            )
        except AlreadyInGameError:
            return

        return game

    @_with_workflow_data
    async def get_multi_device_game(
            self,
            *,
            multi_device_games: 'MultiDeviceGamesController'
    ) -> None:
        return await multi_device_games.get_game_by_user_id(self.id)

    @_with_workflow_data
    async def end_multi_device_game(
            self,
            *,
            multi_device_games: 'MultiDeviceGamesController',
            qr_codes: RedisController[QRCode],
            game_id: UUID | None = None
    ) -> None:
        if game_id is None:
            game: MultiDeviceGame = await self.get_multi_device_game()

            if game is None:
                return

            game_id = game.game_id

        await multi_device_games.remove_game(game_id)
        await qr_codes.remove(game_id)

    @_with_workflow_data
    async def recruit_multi_device_game(
            self,
            callback_query: CallbackQuery,
            *,
            multi_device_games: 'MultiDeviceGamesController',
            qr_codes: RedisController[QRCode],
            player_amount: int
    ) -> None:
        game: MultiDeviceGame | None = await self.create_multi_device_game(player_amount=player_amount)

        if game is None:
            return  # TODO: Error message

        message: Message | None = await self._update_multi_device_game_recruitment_messages(game=game)

        if message is not None:
            await qr_codes.set(BlurredQRCode(file_id=message.photo[0].file_id))

        await callback_query.answer()

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"started recruitment for a multi-device game (game_id={game.game_id})"
        )

        game: MultiDeviceGame | None = await multi_device_games.generate_qr_code(game.game_id)
        message: Message | None = await self._update_multi_device_game_recruitment_messages(game=game)

        if message is not None:
            await qr_codes.set(QRCode(game_id=game.game_id, file_id=message.photo[0].file_id))

    @_with_workflow_data
    async def join_multi_device_game(
            self,
            message: Message,
            *,
            multi_device_games: 'MultiDeviceGamesController',
            game_id: UUID
    ) -> MultiDeviceGame | None:
        self.chat_id = message.chat.id

        try:
            game: MultiDeviceGame = await multi_device_games.join_game(
                game_id,
                self.id
            )
        except APIError as error:
            if isinstance(error, NotFoundError):
                message_text: str = _("message.multi_device.play.recruit.game_not_found")
            elif isinstance(error, GameHasAlreadyStartedError):
                message_text: str = _("message.multi_device.play.recruit.game_has_already_started")
            elif isinstance(error, AlreadyInGameError):
                message_text: str = _("message.multi_device.play.recruit.already_in_game")
            elif isinstance(error, InvalidPlayerAmountError):
                message_text: str = _("message.multi_device.play.recruit.too_many_players")
            else:
                message_text: str = _("message.error")

            await message.answer(text=message_text)
            await message.delete()
            return

        await self._update_multi_device_game_recruitment_messages(game=game, joined_player_id=self.id)

        logger.info(
            f"{message.from_user.first_name} (id={message.from_user.id}) "
            f"joined a multi-device game (game_id={game.game_id})"
        )

    @_with_workflow_data
    async def leave_multi_device_game(
            self,
            *,
            multi_device_games: 'MultiDeviceGamesController',
            update_message: bool = True
    ) -> None:
        game: MultiDeviceGame | None = await self.get_multi_device_game()

        if game is None:
            return  # TODO: Error message

        if self.id == game.host_id:
            await self.end_multi_device_game(game_id=game.game_id)

            tasks: List[Task] = []

            for player in game.players:
                if player.user_id == self.id:
                    continue

                player_bot_user: BotUser = await self.get_bot_user(player.user_id)

                if player_bot_user is None:
                    continue

                with player_bot_user.i18n.use_locale(player_bot_user.locale):
                    tasks.append(
                        create_task(
                            player_bot_user.edit_message(
                                text=_("message.multi_device.play.stop")
                            )
                        )
                    )

            await gather(*tasks)

            logger.info(
                f"{self.first_name} (id={self.telegram_id}) "
                f"finished a multi-device game (game_id={game.game_id})"
            )
        else:
            game: MultiDeviceGame | None = await multi_device_games.leave_game(
                game.game_id,
                self.id
            )

            if update_message:
                await self.edit_message(
                    text=_("message.multi_device.play.leave")
                )

            if game.has_started:
                return

            tasks: List[Task] = []

            for player in game.players:
                if player.user_id == self.id:
                    continue

                player_bot_user: BotUser = await self.get_bot_user(player.user_id)

                if player_bot_user is None:
                    continue

                with player_bot_user.i18n.use_locale(player_bot_user.locale):
                    text, entities = self._create_recruitment_message(game)

                    tasks.append(
                        create_task(
                            player_bot_user.edit_message(
                                text=text,
                                entities=entities,
                                reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(
                                    is_host=player.user_id == game.host_id
                                ),
                                only_edit_caption=True
                            )
                        )
                    )

            await gather(*tasks)

            logger.info(
                f"{self.first_name} (id={self.telegram_id}) "
                f"left a multi-device game (game_id={game.game_id})"
            )

    @_with_workflow_data
    async def start_multi_device_game(
            self,
            callback_query: CallbackQuery,
            *,
            multi_device_games: 'MultiDeviceGamesController',
            qr_codes: RedisController[QRCode]
    ) -> None:
        game: MultiDeviceGame = await self.get_multi_device_game()

        if game is None:
            return  # TODO: Error message

        try:
            game = await multi_device_games.start_game(game.game_id)
        except InvalidPlayerAmountError:
            await callback_query.answer(_("answer.multi_device.play.too_few_players"))
            return

        tasks: List[Task] = []

        for player in game.players:
            player_bot_user: BotUser | None = await self.get_bot_user(player.user_id)

            if player_bot_user is None:
                continue

            with player_bot_user.i18n.use_locale(player_bot_user.locale):
                message_text: LazyProxy = DictFactory.multi_device_role_message().get(player.role)

                tasks.append(
                    create_task(
                        player_bot_user.edit_message(
                            text=message_text.format(
                                secret_word=SecretWordsController.get_secret_word(game.secret_word)
                            ),
                            reply_markup=InlineKeyboardFactory.multi_device_view_role_keyboard(
                                is_host=player.user_id == game.host_id
                            )
                        )
                    )
                )

        await gather(*tasks)
        await callback_query.answer()

        await qr_codes.remove(game.game_id)

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"started a multi-device game (game_id={game.game_id})"
        )

    @_with_workflow_data
    async def finish_multi_device_game(
            self,
            callback_query: CallbackQuery
    ) -> None:
        game: MultiDeviceGame | None = await self.get_multi_device_game()

        if game is None:
            return  # TODO: Error message

        spy: MultiDevicePlayer = [player for player in game.players if player.role == PlayerRole.SPY][0]

        tasks: List[Task] = []

        for player in game.players:
            player_bot_user: BotUser = await self.get_bot_user(player.user_id)

            if player_bot_user is None:
                continue

            with player_bot_user.i18n.use_locale(player_bot_user.locale):
                message_text, entities = self._get_entities(
                    _("message.multi_device.play.finish").format(
                        secret_word=SecretWordsController.get_secret_word(game.secret_word),
                        first_name=spy.first_name
                    ),
                    players=[spy]
                )

                tasks.append(
                    create_task(
                        player_bot_user.edit_message(
                            text=message_text,
                            entities=entities,
                            reply_markup=InlineKeyboardFactory.multi_device_play_again_keyboard(
                                is_host=player.user_id == game.host_id
                            )
                        )
                    )
                )

        await gather(*tasks)

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"finished a multi-device game (game_id={game.game_id})"
        )

    @_with_workflow_data
    async def restart_multi_device_game(
            self,
            callback_query: CallbackQuery,
            *,
            multi_device_games: 'MultiDeviceGamesController',
            qr_codes: RedisController[QRCode]
    ) -> None:
        game: MultiDeviceGame = await self.get_multi_device_game()

        if game is None:
            return  # TODO: Error message

        await qr_codes.remove(game.game_id)
        game: MultiDeviceGame = await multi_device_games.restart_game(game.game_id)

        await self._update_multi_device_game_recruitment_messages(game=game)
        await callback_query.answer()

        logger.info(
            f"{callback_query.from_user.first_name} (id={callback_query.from_user.id}) "
            f"restarted recruitment for a multi-device game (game_id={game.game_id})"
        )

        game: MultiDeviceGame | None = await multi_device_games.generate_qr_code(game.game_id)
        message: Message | None = await self._update_multi_device_game_recruitment_messages(game=game)

        if message is not None:
            await qr_codes.set(QRCode(game_id=game.game_id, file_id=message.photo[0].file_id))

    @_with_workflow_data
    async def _update_multi_device_game_recruitment_messages(
            self,
            *,
            qr_codes: RedisController[QRCode],
            game: MultiDeviceGame,
            joined_player_id: UUID | None = None
    ) -> Message | None:
        tasks: List[Task] = []

        qr_code: InputFile | str | None = await game.get_qr_code(qr_codes)

        for player in game.players:
            player_bot_user: BotUser = await self.get_bot_user(player.user_id)

            if player_bot_user is None:
                continue

            with player_bot_user.i18n.use_locale(player_bot_user.locale):
                text, entities = self._create_recruitment_message(game)

                if joined_player_id is None:
                    coro: Awaitable = player_bot_user.edit_message(
                        text=text,
                        photo=qr_code,
                        entities=entities,
                        reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(
                            is_host=game.host_id == player.user_id
                        )
                    )
                else:
                    if joined_player_id == player.user_id:
                        coro: Awaitable = player_bot_user.new_message(
                            chat_id=player_bot_user.chat_id,
                            text=text,
                            photo=qr_code,
                            entities=entities,
                            reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(
                                is_host=game.host_id == player.user_id
                            )
                        )
                    else:
                        coro: Awaitable = player_bot_user.edit_message(
                            text=text,
                            photo=qr_code,
                            entities=entities,
                            reply_markup=InlineKeyboardFactory.multi_device_recruit_keyboard(
                                is_host=game.host_id == player.user_id
                            ),
                            only_edit_caption=True
                        )

                tasks.append(create_task(coro))

        results: Tuple[Message | None] = await gather(*tasks)

        if results:
            return results[0]

    @classmethod
    def _create_recruitment_message(
            cls,
            game: MultiDeviceGame
    ) -> Tuple[str, List[MessageEntity]]:
        players: List[str] = []

        for index, player in enumerate(game.players):
            if player.user_id == game.host_id:
                players.append(
                    _("message.multi_device.play.recruit.player.host").format(
                        index=index + 1,
                        first_name=player.first_name
                    )
                )
            else:
                players.append(
                    _("message.multi_device.play.recruit.player").format(
                        index=index + 1,
                        first_name=player.first_name
                    )
                )

        return cls._get_entities(
            _("message.multi_device.play.recruit").format(
                players="\n".join(players),
                player_amount=len(game.players),
                max_player_amount=game.player_amount
            ),
            join_url=game.join_url,
            players=game.players
        )

    @staticmethod
    def _get_entities(
            text: str,
            *,
            join_url: str | None = None,
            players: List[MultiDevicePlayer] | None = None
    ) -> Tuple[str, List[MessageEntity]]:
        entities: List[MessageEntity] = []
        tags_to_find: List[str] = ["b", "join", "player"]

        player_index: int = 0

        while True:
            indices: List[int] = [text.find(f"<{tag}>") for tag in tags_to_find]

            closest_tag_index: int = -1
            for index in indices:
                if index == -1:
                    continue
                if closest_tag_index == -1 or index < closest_tag_index:
                    closest_tag_index = index

            if closest_tag_index == -1:
                break

            tag: str = tags_to_find[indices.index(closest_tag_index)]
            open_tag: str = f"<{tag}>"
            close_tag: str = f"</{tag}>"

            open_tag_index: int = text.find(open_tag)
            close_tag_index: int = text.find(close_tag)

            match tag:
                case "b":
                    entities.append(
                        MessageEntity(
                            type=MessageEntityType.BOLD,
                            offset=open_tag_index + 1,
                            length=close_tag_index - open_tag_index - len(open_tag)
                        )
                    )
                case "join":
                    entities.append(
                        MessageEntity(
                            type=MessageEntityType.TEXT_LINK,
                            offset=open_tag_index + 1,
                            length=close_tag_index - open_tag_index - len(open_tag),
                            url=join_url
                        )
                    )
                case "player":
                    entities.append(
                        MessageEntity(
                            type=MessageEntityType.TEXT_MENTION,
                            offset=open_tag_index + 1,
                            length=close_tag_index - open_tag_index - len(open_tag),
                            user=AiogramUser(
                                id=players[player_index].telegram_id,
                                first_name=players[player_index].first_name,
                                is_bot=False
                            )
                        )
                    )
                    entities.append(
                        MessageEntity(
                            type=MessageEntityType.ITALIC,
                            offset=open_tag_index + 1,
                            length=close_tag_index - open_tag_index - len(open_tag)
                        )
                    )
                    player_index += 1

            text = (
                    text[:open_tag_index]
                    + text[open_tag_index + len(open_tag):close_tag_index]
                    + text[close_tag_index + len(close_tag):]
            )

        return text, entities
