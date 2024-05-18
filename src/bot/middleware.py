from typing import Callable, Any, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from src.api import client
from src.bot.cachers import AliasCacher, UserInfo


class UpdateUserInfoMiddleware(BaseMiddleware):
    cache: AliasCacher

    def __init__(self, cache: AliasCacher):
        self.cache = cache

    async def __call__(
        self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], message: Message, data: Dict[str, Any]
    ) -> Any:
        user = message.from_user

        # If the user is not registered, register them.
        if self.cache.get(user.id) is None:
            try:
                await client.create_user(user.id)
            except RuntimeError:
                pass

        # Update information about the user's alias.
        if not self.cache.check(user.id, UserInfo(user.username, user.full_name)):
            cached = self.cache.get(user.id)
            if cached is None or user.username != cached.alias:
                await client.save_user_alias(user.username, user.id)
            if cached is None or user.full_name != cached.fullname:
                await client.save_user_fullname(user.full_name, user.id)
            self.cache.set(user.id, UserInfo(user.username, user.full_name))

        return await handler(message, data)


__all__ = ["UpdateUserInfoMiddleware"]
