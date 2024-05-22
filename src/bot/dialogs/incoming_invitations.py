import dataclasses

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.kbd import Row, Cancel, ListGroup, Button
from aiogram_dialog.widgets.text import Const, Format, List, Case

from src.api import client
from src.api.schemas.method_output_schemas import IncomingInvitationInfo
from src.bot.dialogs.communication import (
    ConfirmationDialogStartData,
    RoomDialogStartData,
    IncomingInvitationDialogStartData,
)
from src.bot.dialogs.states import IncomingInvitationsSG, ConfirmationSG, RoomSG
from src.bot.utils import list_group_finder


class InvitationsWindowConsts:
    INVITATION_LIST_HEADER = """Incoming invitations:\n"""
    NO_INVITATIONS_TEXT = "No invitations :("

    INVITATIONS_LIST_ID = "invitation_list_group"
    ACCEPT_BUTTON_ID = "accept_button"
    REJECT_BUTTON_ID = "reject_button"


class Loader:
    @staticmethod
    async def load_invitations(manager: DialogManager):
        invitations_data = await client.get_incoming_invitations(
            manager.event.from_user.id,
        )
        manager.dialog_data["invitations"] = invitations_data


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        manager.dialog_data["dialog_args"] = IncomingInvitationDialogStartData(**start_data["input"])
        await Loader.load_invitations(manager)

    @staticmethod
    @list_group_finder("invitations")
    async def on_accept_invitation(
        callback: CallbackQuery, widget, manager: DialogManager, invitation: IncomingInvitationInfo
    ):
        if manager.dialog_data["dialog_args"].can_accept is False:
            return

        room_name: str = invitation.room_name
        manager.dialog_data["selected_item"] = invitation

        await manager.start(
            ConfirmationSG.main,
            data={
                "intent": "accept",
                "input": dataclasses.asdict(
                    ConfirmationDialogStartData(
                        f"you want to accept the invitation to {room_name}",
                        "Accepted",
                    )
                ),
            },
            show_mode=ShowMode.SEND,
        )

    @staticmethod
    @list_group_finder("invitations")
    async def on_reject_invitation(
        callback: CallbackQuery, widget, manager: DialogManager, invitation: IncomingInvitationInfo
    ):
        room_name: str = invitation.room_name
        manager.dialog_data["selected_item"] = invitation

        await manager.start(
            ConfirmationSG.main,
            data={
                "intent": "reject",
                "input": dataclasses.asdict(
                    ConfirmationDialogStartData(
                        f"you want to reject the invitation to {room_name}",
                        "Rejected",
                    )
                ),
            },
            show_mode=ShowMode.SEND,
        )

    @staticmethod
    async def on_process_result(start_data: dict, result: bool, manager: DialogManager):
        if not isinstance(start_data, dict):
            return
        if not result:
            await manager.show(ShowMode.SEND)
            return

        invitation: IncomingInvitationInfo = manager.dialog_data["selected_item"]
        user_id = manager.event.from_user.id
        if start_data["intent"] == "accept":
            await client.accept_invitation(invitation.id, user_id)
            await manager.start(
                RoomSG.main,
                data={"input": dataclasses.asdict(RoomDialogStartData(invitation.room, invitation.room_name))},
                mode=StartMode.RESET_STACK,
                show_mode=ShowMode.SEND,
            )
        elif start_data["intent"] == "reject":
            await client.reject_invitation(invitation.id, user_id)
            await Loader.load_invitations(manager)
            await manager.show(ShowMode.SEND)


async def invitations_getter(dialog_manager: DialogManager, **kwargs):
    invitations = dialog_manager.dialog_data["invitations"]
    return {
        "invitations": invitations,
    }


incoming_invitations_dialog = Dialog(
    Window(
        Const(InvitationsWindowConsts.INVITATION_LIST_HEADER),
        Case(
            {
                True: Const(
                    InvitationsWindowConsts.NO_INVITATIONS_TEXT,
                ),
                False: List(
                    Format('{pos}) to "{item.room_name}" from {item.sender.repr}'),
                    items="invitations",
                ),
            },
            selector=lambda data, widget, manager: len(data["invitations"]) == 0,
        ),
        Row(
            Cancel(Const("Back")),
        ),
        ListGroup(
            Row(
                Button(
                    Format("{pos}. {item.room_name}"),
                    on_click=Events.on_accept_invitation,
                    id=InvitationsWindowConsts.ACCEPT_BUTTON_ID,
                ),
                Button(
                    Const("Reject"),
                    on_click=Events.on_reject_invitation,
                    id=InvitationsWindowConsts.REJECT_BUTTON_ID,
                ),
            ),
            id=InvitationsWindowConsts.INVITATIONS_LIST_ID,
            item_id_getter=lambda invitation: invitation.id,
            items=lambda data: data["invitations"],
        ),
        state=IncomingInvitationsSG.list,
        getter=invitations_getter,
    ),
    on_process_result=Events.on_process_result,
    on_start=Events.on_start,
)
