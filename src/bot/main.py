import asyncio
import logging
import os

import dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram_dialog import setup_dialogs

from src.bot.dialogs.create_room import create_room_dialog
from src.bot.dialogs import roomless_dialog
from src.bot.dialogs.room import room_dialog
from src.bot.start_message import start_message_handler


async def main():
    dotenv.load_dotenv(".env")
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.message.register(start_message_handler, CommandStart())
    dp.include_routers(roomless_dialog, create_room_dialog, room_dialog)

    setup_dialogs(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
