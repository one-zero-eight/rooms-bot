import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram_dialog import setup_dialogs

from src.bot.cachers import MemoryAliasCacher
from src.bot.config import get_settings
from src.bot.dialogs import dialogs
from src.bot.middleware import UpdateUserInfoMiddleware
from src.bot.start_message import start_message_handler


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=get_settings().BOT_TOKEN)
    dp = Dispatcher()
    dp.message.middleware(UpdateUserInfoMiddleware(MemoryAliasCacher()))
    dp.message.register(start_message_handler, CommandStart())
    dp.include_routers(*dialogs)

    setup_dialogs(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
