from aiogram.fsm.state import StatesGroup, State


class PromptSG(StatesGroup):
    main = State()


class RoomlessSG(StatesGroup):
    welcome = State()


class RoomSG(StatesGroup):
    main = State()
    roommates = State()
    invitations = State()
    tasks = State()


class IncomingInvitationsSG(StatesGroup):
    list = State()


class ConfirmationSG(StatesGroup):
    main = State()


class OutgoingInvitationsSG(StatesGroup):
    list = State()
    invite = State()


class TaskViewSG(StatesGroup):
    main = State()


class OrderSelectionSG(StatesGroup):
    select = State()


class CreateTaskSG(StatesGroup):
    main = State()


__all__ = [
    "PromptSG",
    "RoomlessSG",
    "RoomSG",
    "IncomingInvitationsSG",
    "ConfirmationSG",
    "OutgoingInvitationsSG",
    "TaskViewSG",
    "OrderSelectionSG",
    "CreateTaskSG",
]
