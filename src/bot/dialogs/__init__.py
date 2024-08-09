from src.bot.dialogs.order.create_order import create_order_dialog
from src.bot.dialogs.rule.create_rule import create_rule_dialog
from src.bot.dialogs.order.order_selection import select_order_dialog
from src.bot.dialogs.roomless import roomless_dialog
from src.bot.dialogs.utils.prompt import prompt_dialog
from src.bot.dialogs.room import room_dialog
from src.bot.dialogs.utils.confirmation import confirmation_dialog
from src.bot.dialogs.invitation.incoming_invitations import incoming_invitations_dialog
from src.bot.dialogs.invitation.outgoing_invitations import outgoing_invitations_dialog
from src.bot.dialogs.rule.rules import rules_dialog
from src.bot.dialogs.periodic_task.periodic_tasks import periodic_tasks_dialog
from src.bot.dialogs.periodic_task.periodic_task_view import periodic_task_view_dialog
from src.bot.dialogs.periodic_task.create_periodic_task import create_periodic_task_dialog

dialogs = [
    roomless_dialog,
    room_dialog,
    prompt_dialog,
    incoming_invitations_dialog,
    confirmation_dialog,
    outgoing_invitations_dialog,
    select_order_dialog,
    periodic_tasks_dialog,
    periodic_task_view_dialog,
    create_periodic_task_dialog,
    create_order_dialog,
    rules_dialog,
    create_rule_dialog,
]

__all__ = [
    "dialogs",
    "roomless_dialog",
    "room_dialog",
    "prompt_dialog",
    "confirmation_dialog",
    "outgoing_invitations_dialog",
    "incoming_invitations_dialog",
    "select_order_dialog",
    "periodic_tasks_dialog",
    "periodic_task_view_dialog",
    "create_periodic_task_dialog",
    "create_order_dialog",
    "rules_dialog",
    "create_rule_dialog",
]
