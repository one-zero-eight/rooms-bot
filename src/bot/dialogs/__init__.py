from src.bot.dialogs.order_selection import select_order_dialog
from src.bot.dialogs.roomless import roomless_dialog
from src.bot.dialogs.prompt import prompt_dialog
from src.bot.dialogs.room import room_dialog
from src.bot.dialogs.confirmation import confirmation_dialog
from src.bot.dialogs.incoming_invitations import incoming_invitations_dialog
from src.bot.dialogs.outgoing_invitations import outgoing_invitations_dialog
from src.bot.dialogs.task_view import task_view_dialog
from src.bot.dialogs.create_task import create_task_dialog

dialogs = [
    roomless_dialog,
    room_dialog,
    prompt_dialog,
    incoming_invitations_dialog,
    confirmation_dialog,
    outgoing_invitations_dialog,
    task_view_dialog,
    select_order_dialog,
    create_task_dialog,
]

__all__ = [
    "dialogs",
    "roomless_dialog",
    "room_dialog",
    "prompt_dialog",
    "confirmation_dialog",
    "outgoing_invitations_dialog",
    "incoming_invitations_dialog",
    "task_view_dialog",
    "select_order_dialog",
    "create_task_dialog",
]
