from typing import Awaitable, Callable, Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.kbd import Row, Button, SwitchTo, Start
from aiogram_dialog.widgets.text import Format, Const, List

from src.api import client
from src.api.schemas.method_output_schemas import DailyInfoResponse, UserInfo
from src.bot.dialogs.dialog_communications import (
    RoomDialogStartData,
    ConfirmationDialogStartData,
    IncomingInvitationDialogStartData,
)
from src.bot.dialogs.states import (
    RoomSG,
    ConfirmationSG,
    RoomlessSG,
    IncomingInvitationsSG,
    OutgoingInvitationsSG,
    RulesSG,
    PeriodicTasksSG,
    ManualTasksSG,
)


class MainWindowConsts:
    REFRESH_BUTTON_ID = "refresh_button"
    ROOMMATES_BUTTON_ID = "roommates_button"
    TASKS_BUTTON_ID = "tasks_button"
    RULES_BUTTON_ID = "rules_button"
    INBOX_BUTTON_ID = "incoming_invitations_button"
    MY_INVITATIONS_BUTTON_ID = "my_invitations_button"
    LEAVE_BUTTON_ID = "leave_button"


class RoommatesWindowConsts:
    BACK_BUTTON_ID = "back_button"


class TaskCategoriesWindowConsts:
    PERIODIC_TASKS_BUTTON_ID = "periodic_tasks_button"
    MANUAL_TASKS_BUTTON_ID = "manual_tasks_button"
    BACK_BUTTON_ID = "back_button"


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        args: RoomDialogStartData = start_data["input"]
        manager.dialog_data["room_info"] = args
        await Loader.load_daily_info(manager)

    @staticmethod
    async def on_leave(callback: CallbackQuery, button, manager: DialogManager):
        room_name: str = manager.dialog_data["room_info"].name
        await manager.start(
            ConfirmationSG.main,
            data={
                "intent": "leave",
                "input": ConfirmationDialogStartData(
                    "you want to leave the room", f'You have left the room "{room_name}"'
                ),
            },
            show_mode=ShowMode.SEND,
        )

    @staticmethod
    async def on_process_result(start_data: dict, result: bool | None, manager: DialogManager):
        if not start_data or not isinstance(start_data, dict):
            return

        if start_data["intent"] == "leave":
            if result is False:
                await manager.show(ShowMode.SEND)
                return

            user_id = manager.event.from_user.id
            await client.leave_room(user_id)
            await manager.start(
                RoomlessSG.welcome,
                mode=StartMode.RESET_STACK,
                show_mode=ShowMode.SEND,
            )

    @staticmethod
    async def on_click_rules(callback: CallbackQuery, button, manager: DialogManager):
        await manager.start(
            RulesSG.list,
            show_mode=ShowMode.EDIT,
            data={"intent": "create_rule"},
        )


class Loader:
    @staticmethod
    def show_decorator(func: Callable[[CallbackQuery, Any, DialogManager], Awaitable]):
        async def wrapper(callback: CallbackQuery, button: Any, manager: DialogManager):
            await func(callback, button, manager)
            await manager.show()

        return wrapper

    @staticmethod
    def load_callback(func: Callable[[DialogManager], Awaitable]):
        async def wrapper(callback: CallbackQuery, button: Any, manager: DialogManager):
            await func(manager)

        return wrapper

    @staticmethod
    async def load_daily_info(manager: DialogManager):
        data = await client.get_daily_info(manager.event.from_user.id)
        manager.dialog_data["daily_info"] = data

    @staticmethod
    async def load_roommates(manager: DialogManager):
        data = await client.get_room_info(manager.event.from_user.id)
        manager.dialog_data["roommates"] = [user for user in data.users if not user.empty()]


async def getter(dialog_manager: DialogManager, **kwargs):
    room_info: RoomDialogStartData = dialog_manager.dialog_data["room_info"]
    daily_info: DailyInfoResponse = dialog_manager.dialog_data["daily_info"]
    user_info: dict[int, UserInfo] = daily_info.user_info
    roommates: list[UserInfo] = dialog_manager.dialog_data.get("roommates", [])
    return {
        "room_id": room_info.id,
        "room_name": room_info.name,
        "periodic_tasks": [
            (t.name, user_info[t.today_executor].fullname if t.today_executor in user_info else str(t.today_executor))
            for t in daily_info.periodic_tasks
        ],
        "manual_tasks": [
            (t.name, user_info[t.today_executor].fullname if t.today_executor in user_info else str(t.today_executor))
            for t in daily_info.manual_tasks
        ],
        "roommates": roommates,
    }


room_dialog = Dialog(
    # Main page
    Window(
        Format("Your room: {room_name}\n"),
        Const("Current duties:"),
        List(
            Format("- {item[0]}: {item[1]}"),
            items="periodic_tasks",
        ),
        List(
            Format("- {item[0]}: {item[1]}"),
            items="manual_tasks",
        ),
        Row(
            Button(
                Const("Refresh"),
                MainWindowConsts.REFRESH_BUTTON_ID,
                on_click=Loader.show_decorator(Loader.load_callback(Loader.load_daily_info)),
            ),
        ),
        Row(
            SwitchTo(
                Const("Roommates"),
                MainWindowConsts.ROOMMATES_BUTTON_ID,
                RoomSG.roommates,
                on_click=Loader.load_callback(Loader.load_roommates),
            ),
            SwitchTo(
                Const("Tasks"),
                id=MainWindowConsts.TASKS_BUTTON_ID,
                state=RoomSG.tasks,
            ),
            Button(
                Const("Rules"),
                id=MainWindowConsts.RULES_BUTTON_ID,
                on_click=Events.on_click_rules,
            ),
        ),
        Row(
            Start(
                Const("Inbox"),
                id=MainWindowConsts.INBOX_BUTTON_ID,
                state=IncomingInvitationsSG.list,
                data={
                    "intent": "inbox",
                    "input": IncomingInvitationDialogStartData(False),
                },
            ),
            Start(
                Const("My invitations"),
                id=MainWindowConsts.MY_INVITATIONS_BUTTON_ID,
                state=OutgoingInvitationsSG.list,
                data={
                    "intent": "sent_invitations",
                },
            ),
            Button(Const("Leave"), MainWindowConsts.LEAVE_BUTTON_ID, on_click=Events.on_leave),
        ),
        getter=getter,
        state=RoomSG.main,
    ),
    # Roommate list
    Window(
        List(
            Format("{pos}. {item.repr}"),
            items="roommates",
        ),
        SwitchTo(
            Const("◀️ Back"),
            RoommatesWindowConsts.BACK_BUTTON_ID,
            RoomSG.main,
            on_click=Loader.load_callback(Loader.load_daily_info),
        ),
        state=RoomSG.roommates,
        getter=getter,
    ),
    # Task category selection
    Window(
        Const("Choose a category:"),
        Start(
            Const("Periodic"),
            TaskCategoriesWindowConsts.PERIODIC_TASKS_BUTTON_ID,
            state=PeriodicTasksSG.list,
        ),
        Start(
            Const("Manual"),
            TaskCategoriesWindowConsts.MANUAL_TASKS_BUTTON_ID,
            state=ManualTasksSG.list,
        ),
        SwitchTo(
            Const("◀️ Back"),
            TaskCategoriesWindowConsts.BACK_BUTTON_ID,
            state=RoomSG.main,
            on_click=Loader.load_callback(Loader.load_daily_info),
        ),
        state=RoomSG.tasks,
    ),
    on_start=Events.on_start,
    on_process_result=Events.on_process_result,
)
