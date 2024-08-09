from aiogram_dialog import ShowMode, DialogManager, Dialog, Window

from src.bot.dialogs.dialog_communications import PromptDialogStartData, CreateTaskForm
from src.bot.dialogs.states import PromptSG, CreateTaskSG, OrderSelectionSG
from src.bot.utils import datetime_validator, parse_datetime


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        manager.dialog_data["form"] = CreateTaskForm()
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
    async def on_process_result(start_data: dict, result: str | None, manager: DialogManager):
        form: CreateTaskForm = manager.dialog_data["form"]
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
                    OrderSelectionSG.select,
                    data={
                        "intent": "select_order",
                    },
                    show_mode=ShowMode.SEND,
                )
            case "select_order":
                if not result[0]:
                    await Events._cancel(manager)
                    return
                form.order_id = result[1]
                await manager.event.bot.send_message(manager.event.message.chat.id, "Created")
                await manager.done((True, form), ShowMode.SEND)


create_task_dialog = Dialog(
    Window(
        state=CreateTaskSG.main,
    ),
    on_start=Events.on_start,
    on_process_result=Events.on_process_result,
)
