from src.bot.dialogs.roomless import roomless_dialog
from src.bot.dialogs.create_room import create_room_dialog
from src.bot.dialogs.room import room_dialog
from src.bot.dialogs.incoming_invitations import incoming_invitations_dialog
from src.bot.dialogs.confirmation import confirmation_dialog


dialogs = [roomless_dialog, room_dialog, create_room_dialog, incoming_invitations_dialog, confirmation_dialog]

__all__ = [
    "dialogs",
    "roomless_dialog",
    "room_dialog",
    "create_room_dialog",
    "incoming_invitations_dialog",
    "confirmation_dialog",
]
