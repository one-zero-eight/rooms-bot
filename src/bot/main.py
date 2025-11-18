import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart, ExceptionTypeFilter
from aiogram.types import ErrorEvent, CallbackQuery
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent

from src.bot.cachers import MemoryAliasCacher
from src.bot.config import get_settings
from src.bot.dialogs import dialogs
from src.bot.middleware import UpdateUserInfoMiddleware
from src.bot.start_message import start_message_handler


async def main():
    logging.basicConfig(level=logging.INFO)
    
    if get_settings().TELEGRAM_PROXY_URL:
        logging.info("Using proxy")
        session = AiohttpSession(proxy=get_settings().TELEGRAM_PROXY_URL)
    else:
        session = None

    bot = Bot(token=get_settings().BOT_TOKEN, session=session)
    dp = Dispatcher()
    dp.message.middleware(UpdateUserInfoMiddleware(MemoryAliasCacher()))
    dp.message.register(start_message_handler, CommandStart())
    dp.include_routers(*dialogs)

    @dp.error(ExceptionTypeFilter(UnknownIntent), F.update.callback_query.as_("callback_query"))
    async def unknown_intent_handler(event: ErrorEvent, callback_query: CallbackQuery):
        await callback_query.answer("Use /start command to restart.")

    setup_dialogs(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
