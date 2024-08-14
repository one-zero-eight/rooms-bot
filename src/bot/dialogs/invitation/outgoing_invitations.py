import re

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Row, Cancel, ListGroup, Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List, Case

from src.api import client
from src.api.schemas.method_output_schemas import SentInvitationInfo
from src.bot.dialogs.dialog_communications import ConfirmationDialogStartData
from src.bot.dialogs.states import OutgoingInvitationsSG, ConfirmationSG
from src.bot.utils import list_group_finder


class InvitationsWindowConsts:
    INVITATION_LIST_HEADER = "Your invitations to this room:\n"
    NO_INVITATIONS_TEXT = "No invitations :("
    INVITE_BUTTON_TEXT = "Invite a person"

    INVITATIONS_LIST_ID = "invitation_list_group"
    INVITE_BUTTON_ID = "invite_button"
    ROOM_NAME_BUTTON_ID = "room_name_button"
    DELETE_BUTTON_ID = "delete_button"


class InviteWindowConsts:
    ENTER_ALIAS_PROMPT = "Enter a user's alias"
    ALIAS_PATTERN = re.compile(r"@?[a-z][a-z0-9_]{4,31}")
    INCORRECT_ALIAS_MESSAGE = "The entered alias is incorrect. Try again."
    INVITATION_SENT_MESSAGE = "The invitation has been sent"

    CANCEL_BUTTON_ID = "cancel_button"
    ENTER_ALIAS_INPUT_ID = "enter_alias_input"


class Loader:
    @staticmethod
    async def load_invitations(manager: DialogManager):
        invitations_data = await client.get_sent_invitations(manager.event.from_user.id)
        manager.dialog_data["invitations"] = invitations_data


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        await Loader.load_invitations(manager)

    @staticmethod
    @list_group_finder("invitations")
    async def on_delete_invitation(
        callback: CallbackQuery, widget, manager: DialogManager, invitation: SentInvitationInfo
    ):
        addressee: str = invitation.addressee
        manager.dialog_data["selected_item"] = invitation

        await manager.start(
            ConfirmationSG.main,
            data={
                "intent": "delete",
                "input": ConfirmationDialogStartData(f"you want to delete the invitation to @{addressee}", "Deleted"),
            },
            show_mode=ShowMode.SEND,
        )

    @staticmethod
    async def on_enter_alias(message: Message, widget, manager: DialogManager, alias: str):
        alias = alias.strip()
        if not InviteWindowConsts.ALIAS_PATTERN.fullmatch(alias.lower()):
            await message.answer(InviteWindowConsts.INCORRECT_ALIAS_MESSAGE)
            return

        if alias[0] == "@":
            alias = alias[1:]
        await client.invite_person(alias, manager.event.from_user.id)
        await message.bot.send_message(message.chat.id, InviteWindowConsts.INVITATION_SENT_MESSAGE)
        await Loader.load_invitations(manager)
        await manager.switch_to(OutgoingInvitationsSG.list, show_mode=ShowMode.SEND)

    @staticmethod
    async def on_process_result(start_data: dict, result: bool, manager: DialogManager):
        if not isinstance(start_data, dict):
            return
        if not result:
            await manager.show(ShowMode.SEND)
            return

        user_id = manager.event.from_user.id
        if start_data["intent"] == "delete":
            invitation: SentInvitationInfo = manager.dialog_data["selected_item"]
            await client.delete_invitation(invitation.id, user_id)
            await Loader.load_invitations(manager)
            await manager.show(ShowMode.SEND)


async def invitations_getter(dialog_manager: DialogManager, **kwargs):
    invitations = dialog_manager.dialog_data["invitations"]
    return {
        "invitations": invitations,
    }


outgoing_invitations_dialog = Dialog(
    Window(
        Const(InvitationsWindowConsts.INVITATION_LIST_HEADER),
        Case(
            {
                True: Const(
                    InvitationsWindowConsts.NO_INVITATIONS_TEXT,
                ),
                False: List(
                    Format("{pos}) to @{item.addressee}"),
                    items="invitations",
                ),
            },
            selector=lambda data, widget, manager: len(data["invitations"]) == 0,
        ),
        Row(
            Cancel(Const("Back")),
        ),
        Row(
            SwitchTo(
                Const(InvitationsWindowConsts.INVITE_BUTTON_TEXT),
                id=InvitationsWindowConsts.INVITE_BUTTON_ID,
                state=OutgoingInvitationsSG.invite,
            ),
        ),
        ListGroup(
            Row(
                Button(
                    Format("{pos}. {item.addressee}"),
                    id=InvitationsWindowConsts.ROOM_NAME_BUTTON_ID,
                ),
                Button(
                    Const("Delete"),
                    on_click=Events.on_delete_invitation,
                    id=InvitationsWindowConsts.DELETE_BUTTON_ID,
                ),
            ),
            id=InvitationsWindowConsts.INVITATIONS_LIST_ID,
            item_id_getter=lambda invitation: invitation.id,
            items="invitations",
        ),
        state=OutgoingInvitationsSG.list,
        getter=invitations_getter,
    ),
    Window(
        Const(InviteWindowConsts.ENTER_ALIAS_PROMPT),
        SwitchTo(
            Const("Cancel"),
            state=OutgoingInvitationsSG.list,
            id=InviteWindowConsts.CANCEL_BUTTON_ID,
        ),
        TextInput(
            on_success=Events.on_enter_alias,
            id=InviteWindowConsts.ENTER_ALIAS_INPUT_ID,
        ),
        state=OutgoingInvitationsSG.invite,
    ),
    on_process_result=Events.on_process_result,
    on_start=Events.on_start,
)
