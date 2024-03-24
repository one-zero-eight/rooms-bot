from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from src.api import client
from src.bot.dialogs.communication import RoomDialogStartData
from src.bot.dialogs.states import RoomlessSG, RoomSG


async def start_message_handler(message: Message, dialog_manager: DialogManager):
    user_id = message.from_user.id
    try:
        await client.create_user(user_id)
    except RuntimeError:
        pass

    try:
        room_info = await client.get_room_info(user_id)
        # noinspection PyTypeChecker
        await dialog_manager.start(
            RoomSG.main,
            data=RoomDialogStartData(room_info.id, room_info.name),
            mode=StartMode.RESET_STACK,
        )
    except RuntimeError:
        await dialog_manager.start(RoomlessSG.welcome, mode=StartMode.RESET_STACK)
