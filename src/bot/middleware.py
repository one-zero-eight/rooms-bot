from typing import Callable, Any, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from src.api import client


class UpdateUserInfoMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], message: Message, data: Dict[str, Any]
    ) -> Any:
        user = message.from_user

        # If the user is not registered, register them.
        try:
            await client.create_user(user.id)
        except RuntimeError:
            pass

        if user.username is not None:
            # Update information about the user's alias.
            await client.save_user_alias(user.username, user.id)

        return await handler(message, data)


__all__ = ["UpdateUserInfoMiddleware"]
