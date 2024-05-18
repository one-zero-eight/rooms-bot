from typing import Callable, Any, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from src.api import client
from src.bot.cachers import AliasCacher


class UpdateUserInfoMiddleware(BaseMiddleware):
    cache: AliasCacher

    def __init__(self, cache: AliasCacher):
        self.cache = cache

    async def __call__(
        self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], message: Message, data: Dict[str, Any]
    ) -> Any:
        user = message.from_user

        # If the user is not registered, register them.
        try:
            await client.create_user(user.id)
        except RuntimeError:
            pass

        # Update information about the user's alias.
        if not self.cache.check(user.id, user.username):
            if user.username is not None:
                await client.save_user_alias(user.username, user.id)
            self.cache.set(user.id, user.username)

        return await handler(message, data)


__all__ = ["UpdateUserInfoMiddleware"]
