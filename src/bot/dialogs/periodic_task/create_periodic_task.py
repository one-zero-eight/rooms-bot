from aiogram_dialog import ShowMode, DialogManager, Dialog, Window

from src.bot.dialogs.dialog_communications import PromptDialogStartData, CreatePeriodicTaskForm, CreateOrderStartData, \
    CreateTaskStartData
from src.bot.dialogs.states import PromptSG, CreatePeriodicTaskSG, CreateOrderSG
from src.bot.utils import datetime_validator, parse_datetime


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        start_data: CreateTaskStartData = start_data["input"]
        manager.dialog_data["user_id"] = start_data.user_id
        manager.dialog_data["form"] = CreatePeriodicTaskForm()
        await manager.start(
            PromptSG.main,
            data={
                "intent": "enter_name",
                "input": PromptDialogStartData("a name for a task"),
            },
            show_mode=ShowMode.EDIT,
        )

    @staticmethod
    async def _cancel(manager: DialogManager):
        await manager.done((False, None), ShowMode.SEND)

    @staticmethod
    async def _prompt_step(intent: str, prompt: PromptDialogStartData, manager: DialogManager):
        await manager.start(
            PromptSG.main,
            data={
                "intent": intent,
                "input": prompt,
            },
            show_mode=ShowMode.SEND,
        )

    @staticmethod
    async def on_process_result(start_data: dict, result: str | int | None, manager: DialogManager):
        form: CreatePeriodicTaskForm = manager.dialog_data["form"]
        # noinspection DuplicatedCode
        match start_data["intent"]:
            case "enter_name":
                if result is None:
                    await Events._cancel(manager)
                    return
                form.name = result
                await Events._prompt_step(
                    "enter_description", PromptDialogStartData("a description", can_skip=True), manager
                )
            case "enter_description":
                if result is None:
                    await Events._cancel(manager)
                    return
                form.description = result if result != "" else None
                await Events._prompt_step(
                    "enter_start_date",
                    PromptDialogStartData("a start date (d.m.Y H:M)", filter=datetime_validator),
                    manager,
                )
            case "enter_start_date":
                if result is None:
                    await Events._cancel(manager)
                    return
                form.start_date = parse_datetime(result)
                await Events._prompt_step(
                    "enter_period",
                    PromptDialogStartData("a period in days", filter=lambda s: s.isdecimal() and int(s) > 0),
                    manager,
                )
            case "enter_period":
                if result is None:
                    await Events._cancel(manager)
                    return
                form.period = int(result)
                await manager.start(
                    CreateOrderSG.first,
                    data={
                        "intent": "create_order",
                        "input": CreateOrderStartData(manager.dialog_data["user_id"])
                    },
                    show_mode=ShowMode.SEND,
                )
            case "create_order":
                if not result[0]:
                    await Events._cancel(manager)
                    return
                form.order_id = result[1]
                await manager.done((True, form), ShowMode.SEND)


create_periodic_task_dialog = Dialog(
    Window(
        state=CreatePeriodicTaskSG.main,
    ),
    on_start=Events.on_start,
    on_process_result=Events.on_process_result,
)
