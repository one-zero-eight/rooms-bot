import asyncio
import logging
import os

import dotenv
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs


dotenv.load_dotenv(".env")

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()


async def main():
    logging.basicConfig(level=logging.INFO)

    setup_dialogs(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
