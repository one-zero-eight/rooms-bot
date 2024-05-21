from aiogram.fsm.state import StatesGroup, State


class CreateRoomSG(StatesGroup):
    enter_name = State()


class RoomlessSG(StatesGroup):
    welcome = State()


class RoomSG(StatesGroup):
    main = State()
    roommates = State()
    invitations = State()


class IncomingInvitationsSG(StatesGroup):
    list = State()


class ConfirmationSG(StatesGroup):
    main = State()


class OutgoingInvitationsSG(StatesGroup):
    list = State()
    invite = State()


__all__ = ["CreateRoomSG", "RoomlessSG", "RoomSG", "IncomingInvitationsSG", "ConfirmationSG", "OutgoingInvitationsSG"]
