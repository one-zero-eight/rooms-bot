from dataclasses import dataclass

from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, Data, ShowMode, StartMode
from aiogram_dialog.widgets.kbd import Row, Button, Select, SwitchTo, Group
from aiogram_dialog.widgets.text import Const, Format, List

from src.api import client
from src.api.schemas.method_output_schemas import IncomingInvitationInfo
from src.bot.dialogs.communication import CreateRoomDialogResult, RoomDialogStartData
from src.bot.dialogs.states import RoomlessSG, CreateRoomSG, RoomSG


class WelcomeWindowConsts:
    WELCOME_MESSAGE = """This is a welcome message\n
You can:
- Accept an invitation to a room
- Create a new room"""

    INVITATIONS_BUTTON_ID = "invitations_button"
    CREATE_ROOM_BUTTON_ID = "create_room_button"


class InvitationsWindowConsts:
    INVITATION_LIST_HEADER = """Incoming invitations:\n"""
    NO_INVITATIONS_TEXT = """No invitations :("""

    SELECT_INVITATIONS_ID = "select_invitation"
    BACK_BUTTON_ID = "back"


async def process_create_room_result(start_data: Data, result: CreateRoomDialogResult, manager: DialogManager):
    if result.created:
        room_id = await client.create_room(result.name, manager.event.from_user.id)
        # noinspection PyTypeChecker
        await manager.start(
            RoomSG.main,
            data=RoomDialogStartData(room_id, result.name),
            mode=StartMode.RESET_STACK,
        )


async def start_creating_room(event: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(CreateRoomSG.enter_name, show_mode=ShowMode.SEND)


@dataclass
class Invitation:
    id: int
    room_name: str
    sender_alias: str
    from_: str


async def invitations_getter(dialog_manager: DialogManager, **kwargs):
    invitations_data = await client.get_incoming_invitations(
        dialog_manager.event.from_user.id,
    )
    n = len(invitations_data)
    invitations: list[Invitation] = []
    i: IncomingInvitationInfo
    for i in invitations_data:
        from_ = f" (from @{i.sender_alias})" if i.sender_alias is not None else ""
        invitations.append(Invitation(id=i.id, room_name=i.room_name, sender_alias=i.sender_alias, from_=from_))
    return {
        "invitation_count": n,
        "invitations": invitations,
    }


async def on_select_invitation(callback: CallbackQuery, widget, manager: DialogManager, item_id: str):
    user_id = manager.event.from_user.id
    try:
        room_id = await client.accept_invitation(item_id, user_id)
        # noinspection PyTypeChecker
        await manager.start(
            RoomSG.main,
            data=RoomDialogStartData(room_id, (await client.get_room_info(user_id)).name),
            mode=StartMode.RESET_STACK,
        )
    except RuntimeError:
        await callback.message.answer("Error happened.")


roomless_dialog = Dialog(
    # Main page
    Window(
        Const(WelcomeWindowConsts.WELCOME_MESSAGE),
        Row(
            SwitchTo(
                Const("Invitations"),
                id=WelcomeWindowConsts.INVITATIONS_BUTTON_ID,
                state=RoomlessSG.invitations,
            ),
            Button(
                Const("Create"),
                WelcomeWindowConsts.CREATE_ROOM_BUTTON_ID,
                on_click=start_creating_room,
            ),
        ),
        state=RoomlessSG.welcome,
    ),
    # Invitations
    Window(
        Const(InvitationsWindowConsts.INVITATION_LIST_HEADER),
        Const(
            InvitationsWindowConsts.NO_INVITATIONS_TEXT,
            when=lambda data, widget, manager: data["invitation_count"] == 0,
        ),
        List(
            Format('{pos}) to "{item.room_name}"{item.from_}'),
            items="invitations",
            when=lambda data, widget, manager: data["invitation_count"] > 0,
        ),
        Row(
            SwitchTo(
                Const("Back"),
                id=InvitationsWindowConsts.BACK_BUTTON_ID,
                state=RoomlessSG.welcome,
            ),
        ),
        Group(
            Select(
                Format("{pos}"),
                id=InvitationsWindowConsts.SELECT_INVITATIONS_ID,
                item_id_getter=lambda invitation: invitation.id,
                items=lambda data: data["invitations"],
                on_click=on_select_invitation,
            ),
            width=5,
        ),
        state=RoomlessSG.invitations,
        getter=invitations_getter,
    ),
    on_process_result=process_create_room_result,
)
