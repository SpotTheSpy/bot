from typing import Dict, Any
from uuid import UUID

from aiogram import Bot

from app.controllers.redis.abstract import RedisController
from app.models.user import BotUser, User


class BotUsersController(RedisController):
    def key(
            self,
            user_id: UUID
    ) -> str:
        return f"bot_user:{user_id}"

    async def set_bot_user(
            self,
            bot_user: BotUser
    ) -> None:
        await self.set(self.key(bot_user.id), bot_user.to_json())

    async def get_bot_user(
            self,
            user_id: UUID,
            bot: Bot
    ) -> BotUser | None:
        user_json: Dict[str, Any] = await self.get(self.key(user_id))

        if user_json is None:
            return

        return BotUser.from_user(
            User.from_json(user_json),
            chat_id=user_json.get("chat_id"),
            message_id=user_json.get("message_id"),
            has_photo=user_json.get("has_photo"),
            bot=bot,
            controller=self
        )

    async def exists_bot_user(
            self,
            user_id: UUID
    ) -> bool:
        return await self.exists(self.key(user_id))

    async def remove_bot_user(
            self,
            user_id: UUID
    ) -> None:
        await self.remove(self.key(user_id))
