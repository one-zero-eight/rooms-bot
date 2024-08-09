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
    rules = State()


class IncomingInvitationsSG(StatesGroup):
    list = State()


class ConfirmationSG(StatesGroup):
    main = State()


class OrderSelectionSG(StatesGroup):
    select = State()


class OutgoingInvitationsSG(StatesGroup):
    list = State()
    invite = State()


class PeriodicTasksSG(StatesGroup):
    list = State()


class PeriodicTaskViewSG(StatesGroup):
    main = State()


class CreatePeriodicTaskSG(StatesGroup):
    main = State()


class CreateOrderSG(StatesGroup):
    first = State()
    multiple = State()


class RulesSG(StatesGroup):
    list = State()
    view = State()


class CreateRuleSG(StatesGroup):
    main = State()


class ManualTasksSG(StatesGroup):
    list = State()


class ManualTaskViewSG(StatesGroup):
    main = State()


class CreateManualTaskSG(StatesGroup):
    main = State()


__all__ = [
    "PromptSG",
    "RoomlessSG",
    "RoomSG",
    "IncomingInvitationsSG",
    "ConfirmationSG",
    "OutgoingInvitationsSG",
    "OrderSelectionSG",
    "PeriodicTasksSG",
    "PeriodicTaskViewSG",
    "CreatePeriodicTaskSG",
    "CreateOrderSG",
    "RulesSG",
    "CreateRuleSG",
    "ManualTasksSG",
    "ManualTaskViewSG",
    "CreateManualTaskSG",
]
