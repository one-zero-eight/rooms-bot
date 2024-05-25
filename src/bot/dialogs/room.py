import dataclasses
from typing import Awaitable, Callable, Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.kbd import Row, Button, SwitchTo, Start, Select, Group
from aiogram_dialog.widgets.text import Format, Const, List

from src.api import client
from src.api.schemas.method_output_schemas import DailyInfoResponse, UserInfo, Task
from src.bot.dialogs.dialog_communications import (
    RoomDialogStartData,
    ConfirmationDialogStartData,
    IncomingInvitationDialogStartData,
    TaskViewDialogStartData,
)
from src.bot.dialogs.states import (
    RoomSG,
    ConfirmationSG,
    RoomlessSG,
    IncomingInvitationsSG,
    OutgoingInvitationsSG,
    TaskViewSG,
)
from src.bot.utils import select_finder


class MainWindowConsts:
    REFRESH_BUTTON_ID = "refresh_button"
    ROOMMATES_BUTTON_ID = "roommates_button"
    TASKS_BUTTON_ID = "tasks_button"
    INBOX_BUTTON_ID = "incoming_invitations_button"
    MY_INVITATIONS_BUTTON_ID = "my_invitations_button"
    LEAVE_BUTTON_ID = "leave_button"


class RoommatesWindowConsts:
    BACK_BUTTON_ID = "back_button"


class TasksWindowConsts:
    HEADER_TEXT = "Tasks:\n"
    NEW_TASK_BUTTON_TEXT = "Add a new task"
    ACTIVE_TASK_SYMBOL = "+"
    INACTIVE_TASK_SYMBOL = "-"

    BACK_BUTTON_ID = "back_button"
    NEW_TASK_BUTTON_ID = "new_task_button"
    TASK_SELECT_ID = "task_select"


@dataclasses.dataclass
class TaskRepresentation:
    id: int
    name: str
    symbol: str


async def getter(dialog_manager: DialogManager, **kwargs):
    room_info: RoomDialogStartData = dialog_manager.dialog_data["room_info"]
    daily_info: DailyInfoResponse = dialog_manager.dialog_data["daily_info"]
    roommates: list[UserInfo] = dialog_manager.dialog_data.get("roommates", [])
    task_data: list[Task] = dialog_manager.dialog_data.get("tasks", [])
    tasks = [
        TaskRepresentation(
            t.id,
            t.name,
            TasksWindowConsts.INACTIVE_TASK_SYMBOL if t.inactive else TasksWindowConsts.ACTIVE_TASK_SYMBOL,
        )
        for t in task_data
    ]
    return {
        "room_id": room_info.id,
        "room_name": room_info.name,
        "daily_info": daily_info,
        "roommates": roommates,
        "tasks": tasks,
    }


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
        if not isinstance(start_data, dict):
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

        if start_data["intent"] == "view_task":
            await Loader.load_tasks(manager)
            await manager.show()

    @staticmethod
    @select_finder("tasks")
    async def on_select_task(callback: CallbackQuery, widget, manager: DialogManager, task: TaskRepresentation):
        await manager.start(
            TaskViewSG.main,
            data={
                "intent": "view_task",
                "input": TaskViewDialogStartData(task.id),
            },
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

    @staticmethod
    async def load_tasks(manager: DialogManager):
        data = await client.get_tasks(manager.event.from_user.id)
        manager.dialog_data["tasks"] = data


room_dialog = Dialog(
    # Main page
    Window(
        Format("Your room: {room_name}\nID: {room_id}\n\n{daily_info}"),
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
                on_click=Loader.load_callback(Loader.load_tasks),
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
            Const("Back"),
            RoommatesWindowConsts.BACK_BUTTON_ID,
            RoomSG.main,
            on_click=Loader.load_callback(Loader.load_daily_info),
        ),
        state=RoomSG.roommates,
        getter=getter,
    ),
    # Task list
    Window(
        Const(TasksWindowConsts.HEADER_TEXT),
        SwitchTo(
            Const("Back"),
            RoommatesWindowConsts.BACK_BUTTON_ID,
            RoomSG.main,
            on_click=Loader.load_callback(Loader.load_daily_info),
        ),
        Button(
            Const(TasksWindowConsts.NEW_TASK_BUTTON_TEXT),
            id=TasksWindowConsts.NEW_TASK_BUTTON_ID,
            # state=NewTaskSG.enter_start_date,
        ),
        Group(
            Select(
                Format("[{item.symbol}] {item.name}"),
                id=TasksWindowConsts.TASK_SELECT_ID,
                item_id_getter=lambda item: item.id,
                items="tasks",
                on_click=Events.on_select_task,
            ),
            width=2,
        ),
        state=RoomSG.tasks,
        getter=getter,
    ),
    on_start=Events.on_start,
    on_process_result=Events.on_process_result,
)
