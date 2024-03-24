from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, Data, ShowMode, StartMode
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Row, Button

from src.api import client
from src.bot.dialogs.communication import CreateRoomDialogResult, RoomDialogStartData
from src.bot.dialogs.states import RoomlessSG, CreateRoomSG, RoomSG

WELCOME_MESSAGE = """This is a welcome message

You can:
- Accept an invitation to a room
- Create a new room"""

INVITATIONS_BUTTON_ID = "invitations_button"
CREATE_ROOM_BUTTON_ID = "create_room_button"


async def process_result(start_data: Data, result: CreateRoomDialogResult, dialog_manager: DialogManager):
    if result.ok:
        room_id = await client.create_room(result.name, dialog_manager.event.from_user.id)
        # noinspection PyTypeChecker
        await dialog_manager.start(
            RoomSG.main, data=RoomDialogStartData(room_id, result.name), mode=StartMode.RESET_STACK
        )


async def start_creating_room(event: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(CreateRoomSG.enter_name, show_mode=ShowMode.SEND)


roomless_dialog = Dialog(
    Window(
        Const(WELCOME_MESSAGE),
        Row(
            Button(Const("Invitations"), INVITATIONS_BUTTON_ID),
            Button(
                Const("Create"),
                CREATE_ROOM_BUTTON_ID,
                on_click=start_creating_room,
            ),
        ),
        state=RoomlessSG.welcome,
    ),
    on_process_result=process_result,
)
