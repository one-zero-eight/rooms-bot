from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, SubManager

from src.api.schemas.method_output_schemas import SentInvitationInfo, IncomingInvitationInfo


# A decorator for ListGroup that finds the selected item in the list of invitations
def select_invitation(func):
    async def wrapped(callback: CallbackQuery, widget, manager: DialogManager):
        assert isinstance(manager, SubManager)

        invitations: list[SentInvitationInfo | IncomingInvitationInfo] = manager.dialog_data["invitations"]
        for i in invitations:
            if i.id == int(manager.item_id):
                manager.dialog_data["selected_item"] = i
                break
        else:
            raise RuntimeError("Selected non-existent room")

        await func(callback, widget, manager)

    return wrapped
