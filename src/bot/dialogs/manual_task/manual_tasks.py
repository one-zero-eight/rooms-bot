from dataclasses import dataclass, asdict

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window, Dialog, ShowMode
from aiogram_dialog.widgets.kbd import Button, Group, Select, Cancel
from aiogram_dialog.widgets.text import Const, Format

from src.api import client
from src.api.schemas.method_input_schemas import CreateManualTaskBody
from src.api.schemas.method_output_schemas import ManualTaskInfo
from src.bot.dialogs.dialog_communications import CreateManualTaskForm, TaskViewDialogStartData, CreateTaskStartData
from src.bot.dialogs.states import ManualTasksSG, CreateManualTaskSG, ManualTaskViewSG
from src.bot.utils import select_finder


class TasksWindowConsts:
    HEADER_TEXT = "Manual tasks are done by people one by one independently of time."
    NEW_TASK_BUTTON_TEXT = "Add a new task"
    ACTIVE_TASK_SYMBOL = "+"
    INACTIVE_TASK_SYMBOL = "-"

    BACK_BUTTON_ID = "back_button"
    NEW_TASK_BUTTON_ID = "new_task_button"
    TASK_SELECT_ID = "task_select"


@dataclass
class TaskRepresentation:
    id: int
    name: str
    symbol: str


class Loader:
    @staticmethod
    async def load_tasks(manager: DialogManager):
        data: list[ManualTaskInfo] = await client.get_manual_tasks(manager.event.from_user.id)
        manager.dialog_data["tasks"] = data


class Events:
    @staticmethod
    async def on_start(start_data, manager: DialogManager):
        await Loader.load_tasks(manager)

    @staticmethod
    @select_finder("tasks")
    async def on_select_task(callback: CallbackQuery, widget, manager: DialogManager, task: ManualTaskInfo):
        await manager.start(
            ManualTaskViewSG.main, data={"intent": "view_task", "input": TaskViewDialogStartData(task.id)}
        )

    @staticmethod
    async def on_create_task(callback: CallbackQuery, widget, manager: DialogManager):
        await manager.start(
            data={
                "intent": "create_task",
                "input": CreateTaskStartData(callback.from_user.id),
            },
            state=CreateManualTaskSG.main,
            show_mode=ShowMode.SEND,
        )

    @staticmethod
    async def on_process_result(start_data: dict, result: tuple[bool, CreateManualTaskForm], manager: DialogManager):
        if not start_data or not isinstance(start_data, dict):
            return

        if start_data["intent"] == "create_task":
            if not result[0]:
                return
            form: CreateManualTaskForm = result[1]
            await client.create_manual_task(CreateManualTaskBody(**asdict(form)), manager.event.from_user.id)
            await manager.event.bot.send_message(manager.event.message.chat.id, "Created")
            # no update is required because on_process_result happens before the dialog is re-rendered

        await Loader.load_tasks(manager)


# noinspection DuplicatedCode
async def list_getter(dialog_manager: DialogManager, **kwargs):
    task_data: list[ManualTaskInfo] = dialog_manager.dialog_data.get("tasks", [])
    tasks = [
        TaskRepresentation(
            t.id,
            t.name,
            TasksWindowConsts.INACTIVE_TASK_SYMBOL if t.inactive else TasksWindowConsts.ACTIVE_TASK_SYMBOL,
        )
        for t in task_data
    ]
    return {
        "tasks": tasks,
    }


manual_tasks_dialog = Dialog(
    # Task list
    Window(
        Const(TasksWindowConsts.HEADER_TEXT),
        Button(
            Const(TasksWindowConsts.NEW_TASK_BUTTON_TEXT),
            id=TasksWindowConsts.NEW_TASK_BUTTON_ID,
            on_click=Events.on_create_task,
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
        Cancel(
            Const("◀️ Back"),
            TasksWindowConsts.BACK_BUTTON_ID,
        ),
        state=ManualTasksSG.list,
        getter=list_getter,
    ),
    on_start=Events.on_start,
    on_process_result=Events.on_process_result,
)
