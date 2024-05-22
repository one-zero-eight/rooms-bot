from dataclasses import dataclass
from datetime import datetime

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Format, Const, List, Multi

from src.api import client
from src.api.schemas.method_output_schemas import UserInfo, TaskInfoResponse
from src.bot.dialogs.communication import TaskViewDialogStartData
from src.bot.dialogs.states import TaskViewSG


class MainWindowConsts:
    TASK_VIEW_FORMAT = """Name: {task.name}
Start date: {task.start_date_repr}
Period (in days): {task.period}
Description: {task.description}"""
    DATE_FORMAT = "%d.%m.%Y %H:%M"
    ORDER_HEADER = "Order:"
    ORDER_ITEM_FORMAT = "{pos}) {item.fullname}"

    BACK_BUTTON_ID = "back_button"


@dataclass
class TaskRepresentation:
    name: str
    description: str
    start_date: datetime
    period: int

    @property
    def start_date_repr(self) -> str:
        return self.start_date.strftime(MainWindowConsts.DATE_FORMAT)


class Loader:
    @staticmethod
    async def load_task_info(manager: DialogManager):
        user_id = manager.event.from_user.id
        task_id = manager.dialog_data["task_id"]

        task_data: TaskInfoResponse = await client.get_task_info(task_id, user_id)
        manager.dialog_data["task"] = task_data

        if task_data.order_id is None:
            manager.dialog_data["executors"] = None
        else:
            order_data = await client.get_order_info(task_data.order_id, user_id)
            manager.dialog_data["executors"] = order_data.users


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        task_id = TaskViewDialogStartData(**start_data["input"]).task_id
        manager.dialog_data["task_id"] = task_id
        await Loader.load_task_info(manager)


async def getter(dialog_manager: DialogManager, **kwargs):
    task: TaskInfoResponse = dialog_manager.dialog_data["task"]
    executors: list[UserInfo] = dialog_manager.dialog_data["executors"]

    return {
        "task": TaskRepresentation(task.name, task.description, task.start_date, task.period),
        "executors": executors,
    }


task_view_dialog = Dialog(
    Window(
        Format(MainWindowConsts.TASK_VIEW_FORMAT),
        Multi(
            Const(MainWindowConsts.ORDER_HEADER),
            List(
                Format(MainWindowConsts.ORDER_ITEM_FORMAT),
                items="executors",
            ),
            when="executors",
        ),
        Cancel(Const("Back"), MainWindowConsts.BACK_BUTTON_ID),
        state=TaskViewSG.main,
        getter=getter,
    ),
    on_start=Events.on_start,
)
