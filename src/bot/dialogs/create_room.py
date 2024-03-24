from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs.communication import CreateRoomDialogResult
from src.bot.dialogs.states import CreateRoomSG


NAME_INPUT_ID = "name_input"


async def text_handler(message: Message, widget, dialog_manager: DialogManager, _):
    await dialog_manager.done(CreateRoomDialogResult(name=message.text), show_mode=ShowMode.SEND)


create_room_dialog = Dialog(
    Window(
        Const("Enter a room's name"),
        Cancel(result=CreateRoomDialogResult(name=None, ok=False)),
        TextInput(NAME_INPUT_ID, on_success=text_handler),
        state=CreateRoomSG.enter_name,
    )
)
