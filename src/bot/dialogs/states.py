from aiogram.fsm.state import StatesGroup, State


class CreateRoomSG(StatesGroup):
    enter_name = State()


class RoomlessSG(StatesGroup):
    welcome = State()
    invitations = State()


class RoomSG(StatesGroup):
    main = State()
