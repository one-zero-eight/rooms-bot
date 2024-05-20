import dataclasses

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, SubManager, ShowMode, StartMode
from aiogram_dialog.widgets.kbd import Row, Cancel, ListGroup, Button
from aiogram_dialog.widgets.text import Const, Format, List, Case

from src.api import client
from src.api.schemas.method_output_schemas import IncomingInvitationInfo
from src.bot.dialogs.communication import ConfirmationDialogStartData, RoomDialogStartData
from src.bot.dialogs.states import IncomingInvitationsSG, ConfirmationSG, RoomSG


class InvitationsWindowConsts:
    INVITATION_LIST_HEADER = """Incoming invitations:\n"""
    NO_INVITATIONS_TEXT = "No invitations :("
    INVITE_BUTTON_TEXT = "Invite a person"

    INVITATIONS_LIST_ID = "invitation_list_group"
    INVITE_BUTTON_ID = "invite_button"
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
    async def on_start(_, manager: DialogManager):
        await Loader.load_invitations(manager)

    @staticmethod
    def _select_invitation(func):
        async def wrapped(callback: CallbackQuery, widget, manager: DialogManager):
            assert isinstance(manager, SubManager)

            invitations: list[IncomingInvitationInfo] = manager.dialog_data["invitations"]
            for i in invitations:
                if i.id == int(manager.item_id):
                    manager.dialog_data["selected_item"] = i
                    break
            else:
                raise RuntimeError("Selected non-existent room")

            await func(callback, widget, manager)

        return wrapped

    @staticmethod
    @_select_invitation
    async def on_accept_invitation(callback: CallbackQuery, widget, manager: DialogManager):
        invitation: IncomingInvitationInfo = manager.dialog_data["selected_item"]
        room_name: str = invitation.room_name

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
    @_select_invitation
    async def on_reject_invitation(callback: CallbackQuery, widget, manager: DialogManager):
        invitation: IncomingInvitationInfo = manager.dialog_data["selected_item"]
        room_name: str = invitation.room_name

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
        "invitation_count": len(invitations),
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
            selector=lambda data, widget, manager: data["invitation_count"] == 0,
        ),
        Row(
            Cancel(Const("Back")),
        ),
        # Row(
        #     SwitchTo(
        #         Const(InvitationsWindowConsts.INVITE_BUTTON_TEXT),
        #         id=InvitationsWindowConsts.INVITE_BUTTON_ID,
        #         state=InvitationsSG.invite,
        #     ),
        # ),
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
