from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Format

from src.bot.dialogs.communication import RoomDialogStartData
from src.bot.dialogs.states import RoomSG


async def getter(dialog_manager: DialogManager):
    room_info: RoomDialogStartData = dialog_manager.dialog_data["room_info"]
    return {
        "room_id": room_info.id,
        "room_name": room_info.name,
    }


async def on_start(start_data: RoomDialogStartData, dialog_manager: DialogManager):
    dialog_manager.dialog_data["room_info"] = start_data


room_dialog = Dialog(
    Window(
        Format("Your room: {room_name}\nID: {room_id}"),
        getter=getter,
        state=RoomSG.main,
    ),
    on_start=on_start,
)
