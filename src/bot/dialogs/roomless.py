import dataclasses

from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, Data, ShowMode, StartMode
from aiogram_dialog.widgets.kbd import Row, Button, Start
from aiogram_dialog.widgets.text import Const

from src.api import client
from src.bot.dialogs.communication import CreateRoomDialogResult, RoomDialogStartData
from src.bot.dialogs.states import RoomlessSG, CreateRoomSG, RoomSG, IncomingInvitationsSG


class WelcomeWindowConsts:
    WELCOME_MESSAGE = """This is a welcome message\n
You can:
- Accept an invitation to a room
- Create a new room"""

    INVITATIONS_BUTTON_ID = "invitations_button"
    CREATE_ROOM_BUTTON_ID = "create_room_button"


async def process_create_room_result(start_data: Data, result: CreateRoomDialogResult, manager: DialogManager):
    if not start_data:
        return

    if start_data["intent"] == "create_room":
        if result.created:
            room_id = await client.create_room(result.name, manager.event.from_user.id)
            await manager.start(
                RoomSG.main,
                data={"input": dataclasses.asdict(RoomDialogStartData(room_id, result.name))},
                mode=StartMode.RESET_STACK,
            )


async def start_creating_room(event: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(CreateRoomSG.enter_name, data={"intent": "create_room"}, show_mode=ShowMode.SEND)


roomless_dialog = Dialog(
    # Main page
    Window(
        Const(WelcomeWindowConsts.WELCOME_MESSAGE),
        Row(
            Start(
                Const("Invitations"),
                id=WelcomeWindowConsts.INVITATIONS_BUTTON_ID,
                state=IncomingInvitationsSG.list,
            ),
            Button(
                Const("Create"),
                WelcomeWindowConsts.CREATE_ROOM_BUTTON_ID,
                on_click=start_creating_room,
            ),
        ),
        state=RoomlessSG.welcome,
    ),
    on_process_result=process_create_room_result,
)
