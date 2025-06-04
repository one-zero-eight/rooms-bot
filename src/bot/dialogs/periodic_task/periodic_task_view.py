import re
from dataclasses import dataclass
from datetime import datetime

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Cancel, Row, Button
from aiogram_dialog.widgets.text import Format, Const, Jinja, List, Case, Multi

from src.api import client
from src.api.schemas.method_input_schemas import ModifyTaskBody, RemoveTaskParametersBody
from src.api.schemas.method_output_schemas import TaskCurrent, UserInfo, TaskInfoResponse
from src.bot.dialogs.dialog_communications import (
    TaskViewDialogStartData,
    ConfirmationDialogStartData,
    PromptDialogStartData,
    CreateOrderStartData,
)
from src.bot.dialogs.states import PeriodicTaskViewSG, ConfirmationSG, PromptSG, CreateOrderSG
from src.bot.utils import parse_datetime, datetime_validator


class MainWindowConsts:
    TASK_VIEW_FORMAT = """Name: {task.name}
Start date: {task.start_date_repr}
Period (in days): {task.period}"""
    DESCRIPTION_FORMAT = "Description: {task.description}"
    DATE_FORMAT = "%d.%m.%Y %H:%M"
    ORDER_HEADER = "Order: "
    ORDER_ITEM_FORMAT = "{pos}) {item.fullname}"
    ORDER_CURRENT_ITEM_FORMAT = "<u>{{pos}}) {{item.fullname}}</u>"
    MISSING_ORDER_TEXT = "none selected"

    NAME_INPUT_PATTERN = re.compile(r".+")
    DESCRIPTION_INPUT_PATTERN = re.compile(r".+(?:\n\r?.+)*")

    @staticmethod
    def period_filter(s: str):
        return s.isdecimal() and int(s) > 0

    BACK_BUTTON_ID = "back_button"
    EDIT_NAME_BUTTON_ID = "edit_name_button"
    EDIT_DESCRIPTION_BUTTON_ID = "edit_description_button"
    EDIT_START_DATE_BUTTON_ID = "edit_start_date_button"
    EDIT_PERIOD_BUTTON_ID = "edit_period_button"
    EDIT_ORDER_BUTTON_ID = "edit_order_button"
    DELETE_BUTTON_ID = "delete_button"


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
            manager.dialog_data["current_executor"] = None
        else:
            order_data = await client.get_order_info(task_data.order_id, user_id)
            manager.dialog_data["executors"] = order_data.users
            current: TaskCurrent | None = await client.get_task_current_executor(task_id, user_id)
            manager.dialog_data["current_executor"] = current


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        args: TaskViewDialogStartData = start_data["input"]
        manager.dialog_data["task_id"] = args.task_id
        await Loader.load_task_info(manager)

    @staticmethod
    async def on_delete_task(callback: CallbackQuery, widget, manager: DialogManager):
        await manager.start(
            ConfirmationSG.main,
            data={
                "intent": "delete",
                "input": ConfirmationDialogStartData("delete the task", yes_message="The task has been deleted"),
            },
            show_mode=ShowMode.SEND,
        )

    @staticmethod
    async def _prompt_string(intent: str, prompt: PromptDialogStartData, manager: DialogManager):
        await manager.start(
            PromptSG.main,
            data={"intent": intent, "input": prompt},
            show_mode=ShowMode.SEND,
        )

    @staticmethod
    async def on_edit_name(callback: CallbackQuery, widget, manager: DialogManager):
        await Events._prompt_string(
            "edit_name", PromptDialogStartData("a new name", filter=MainWindowConsts.NAME_INPUT_PATTERN), manager
        )

    @staticmethod
    async def on_edit_description(callback: CallbackQuery, widget, manager: DialogManager):
        await Events._prompt_string(
            "edit_description",
            PromptDialogStartData(
                "a new description", filter=MainWindowConsts.DESCRIPTION_INPUT_PATTERN, can_skip=True
            ),
            manager,
        )

    @staticmethod
    async def on_edit_start_date(callback: CallbackQuery, widget, manager: DialogManager):
        await Events._prompt_string(
            "edit_start_date",
            PromptDialogStartData("a new start date", filter=datetime_validator),
            manager,
        )

    @staticmethod
    async def on_edit_period(callback: CallbackQuery, widget, manager: DialogManager):
        await Events._prompt_string(
            "edit_period", PromptDialogStartData("a new period", filter=MainWindowConsts.period_filter), manager
        )

    @staticmethod
    async def on_edit_order(callback: CallbackQuery, widget, manager: DialogManager):
        await manager.start(
            CreateOrderSG.first,
            data={"intent": "edit_order", "input": CreateOrderStartData(callback.from_user.id)},
            show_mode=ShowMode.SEND,
        )

    @staticmethod
    async def on_process_result(
        start_data: dict, result: bool | str | tuple[bool, int | None] | None, manager: DialogManager
    ):
        if not isinstance(start_data, dict):
            return

        task_id = manager.dialog_data["task_id"]
        user_id = manager.event.from_user.id
        match start_data["intent"]:
            case "delete":
                if result:
                    await client.delete_task(task_id, user_id)
                    await manager.done(show_mode=ShowMode.SEND)
                    return
                await manager.show(ShowMode.SEND)
            case "edit_name":
                if result is not None:
                    await client.modify_task(ModifyTaskBody(id=task_id, name=result), user_id)
                    await Loader.load_task_info(manager)
                await manager.show(ShowMode.SEND)
            case "edit_description":
                if result is not None:
                    if result == "":
                        await client.remove_task_parameters(
                            RemoveTaskParametersBody(id=task_id, description=True), user_id
                        )
                    else:
                        await client.modify_task(ModifyTaskBody(id=task_id, description=result), user_id)
                    await Loader.load_task_info(manager)
                await manager.show(ShowMode.SEND)
            case "edit_start_date":
                if result is not None:
                    await client.modify_task(ModifyTaskBody(id=task_id, start_date=parse_datetime(result)), user_id)
                    await Loader.load_task_info(manager)
                await manager.show(ShowMode.SEND)
            case "edit_period":
                if result is not None:
                    await client.modify_task(ModifyTaskBody(id=task_id, period=result), user_id)
                    await Loader.load_task_info(manager)
                await manager.show(ShowMode.SEND)
            case "edit_order":
                if not result[0]:
                    await manager.show(ShowMode.SEND)
                    return
                old_order_id = manager.dialog_data["task"].order_id
                if old_order_id is not None:
                    await client.delete_order(old_order_id, user_id)
                if result[1] is None:
                    await client.remove_task_parameters(RemoveTaskParametersBody(id=task_id, order_id=True), user_id)
                else:
                    await client.modify_task(ModifyTaskBody(id=task_id, order_id=result[1]), user_id)
                await Loader.load_task_info(manager)
                await manager.show(ShowMode.SEND)


async def getter(dialog_manager: DialogManager, **kwargs):
    task: TaskInfoResponse = dialog_manager.dialog_data["task"]
    executors: list[UserInfo] = dialog_manager.dialog_data["executors"]
    current_index = current.number if (current := dialog_manager.dialog_data["current_executor"]) else -1

    return {
        "task": TaskRepresentation(task.name, task.description, task.start_date, task.period),
        "executors": executors,
        "current_index": current_index,
    }


periodic_task_view_dialog = Dialog(
    Window(
        Format(MainWindowConsts.TASK_VIEW_FORMAT),
        Format(MainWindowConsts.DESCRIPTION_FORMAT, when=lambda data, w, m: data["task"].description),
        Case(
            {
                False: Const(MainWindowConsts.ORDER_HEADER + MainWindowConsts.MISSING_ORDER_TEXT),
                True: Multi(
                    Const(MainWindowConsts.ORDER_HEADER),
                    List(
                        Case(
                            {
                                False: Format(MainWindowConsts.ORDER_ITEM_FORMAT),
                                True: Jinja(MainWindowConsts.ORDER_CURRENT_ITEM_FORMAT),
                            },
                            selector=lambda data, w, m: data["data"]["current_index"] == data["pos0"],
                        ),
                        items="executors",
                    ),
                ),
            },
            selector=lambda data, w, m: bool(data["executors"]),
        ),
        Row(
            Button(
                Const("Edit name"),
                id=MainWindowConsts.EDIT_NAME_BUTTON_ID,
                on_click=Events.on_edit_name,
            ),
            Button(
                Const("Edit description"),
                id=MainWindowConsts.EDIT_DESCRIPTION_BUTTON_ID,
                on_click=Events.on_edit_description,
            ),
        ),
        Row(
            Button(
                Const("Edit start date"),
                id=MainWindowConsts.EDIT_START_DATE_BUTTON_ID,
                on_click=Events.on_edit_start_date,
            ),
            Button(
                Const("Edit period"),
                id=MainWindowConsts.EDIT_PERIOD_BUTTON_ID,
                on_click=Events.on_edit_period,
            ),
        ),
        Row(
            Button(
                Const("Delete"),
                id=MainWindowConsts.DELETE_BUTTON_ID,
                on_click=Events.on_delete_task,
            ),
            Button(
                Const("Edit order"),
                id=MainWindowConsts.EDIT_ORDER_BUTTON_ID,
                on_click=Events.on_edit_order,
            ),
        ),
        Cancel(Const("◀️ Back"), MainWindowConsts.BACK_BUTTON_ID),
        parse_mode="HTML",
        state=PeriodicTaskViewSG.main,
        getter=getter,
    ),
    on_start=Events.on_start,
    on_process_result=Events.on_process_result,
)
