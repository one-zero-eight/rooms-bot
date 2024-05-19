from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Row, Button, SwitchTo
from aiogram_dialog.widgets.text import Format, Const, List

from src.api import client
from src.api.schemas.method_output_schemas import DailyInfoResponse, UserInfo
from src.bot.dialogs.communication import RoomDialogStartData
from src.bot.dialogs.states import RoomSG


class MainWindowConsts:
    REFRESH_BUTTON_ID = "refresh_button"
    ROOMMATES_BUTTON_ID = "roommates_button"
    TASKS_BUTTON_ID = "tasks_button"
    INVITATIONS_BUTTON_ID = "invitations_button"
    LEAVE_BUTTON_ID = "leave_button"


class RoommatesWindowConsts:
    BACK_BUTTON_ID = "back_button"


async def getter(dialog_manager: DialogManager, **kwargs):
    room_info: RoomDialogStartData = dialog_manager.dialog_data["room_info"]
    daily_info: DailyInfoResponse = dialog_manager.dialog_data["daily_info"]
    roommates: list[UserInfo] = dialog_manager.dialog_data.get("roommates", [])
    return {
        "room_id": room_info.id,
        "room_name": room_info.name,
        "daily_info": daily_info,
        "roommates": roommates,
    }


async def on_start(start_data: RoomDialogStartData, manager: DialogManager):
    manager.dialog_data["room_info"] = start_data
    await Loader.load_daily_info(manager)


class Loader:
    @staticmethod
    def show_decorator(func):
        async def wrapper(callback: CallbackQuery, button: Button, manager: DialogManager):
            await func(callback, button, manager)
            await manager.show()

        return wrapper

    @staticmethod
    async def daily_info_callback(callback: CallbackQuery, button: Button, manager: DialogManager):
        await Loader.load_daily_info(manager)

    @staticmethod
    async def roommates_callback(callback: CallbackQuery, button: Button, manager: DialogManager):
        await Loader.load_roommates(manager)

    @staticmethod
    async def load_daily_info(manager: DialogManager):
        data = await client.get_daily_info(manager.event.from_user.id)
        manager.dialog_data["daily_info"] = data

    @staticmethod
    async def load_roommates(manager: DialogManager):
        data = await client.get_room_info(manager.event.from_user.id)
        manager.dialog_data["roommates"] = [user for user in data.users if not user.empty()]


room_dialog = Dialog(
    Window(
        Format("Your room: {room_name}\nID: {room_id}\n\n{daily_info}"),
        Row(
            Button(
                Const("Refresh"),
                MainWindowConsts.REFRESH_BUTTON_ID,
                on_click=Loader.show_decorator(Loader.daily_info_callback),
            ),
        ),
        Row(
            SwitchTo(
                Const("Roommates"),
                MainWindowConsts.ROOMMATES_BUTTON_ID,
                RoomSG.roommates,
                on_click=Loader.roommates_callback,
            ),
            Button(Const("Tasks"), MainWindowConsts.TASKS_BUTTON_ID),
        ),
        Row(
            Button(Const("My invitations"), MainWindowConsts.INVITATIONS_BUTTON_ID),
            Button(Const("Leave"), MainWindowConsts.LEAVE_BUTTON_ID),
        ),
        getter=getter,
        state=RoomSG.main,
    ),
    Window(
        List(
            Format("{pos}. {item.repr}"),
            items="roommates",
        ),
        SwitchTo(
            Const("Back"),
            RoommatesWindowConsts.BACK_BUTTON_ID,
            RoomSG.main,
            on_click=Loader.daily_info_callback,
        ),
        state=RoomSG.roommates,
        getter=getter,
    ),
    on_start=on_start,
)
