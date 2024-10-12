from aiogram_dialog import ShowMode, DialogManager, Dialog, Window

from src.bot.dialogs.dialog_communications import (
    PromptDialogStartData,
    CreateManualTaskForm,
    CreateOrderStartData,
    CreateTaskStartData,
)
from src.bot.dialogs.states import PromptSG, CreateManualTaskSG, CreateOrderSG


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        start_data: CreateTaskStartData = start_data["input"]
        manager.dialog_data["user_id"] = start_data.user_id
        manager.dialog_data["form"] = CreateManualTaskForm()
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
    async def on_process_result(start_data: dict, result: str | int | None, manager: DialogManager):
        form: CreateManualTaskForm = manager.dialog_data["form"]
        # noinspection DuplicatedCode
        match start_data["intent"]:
            case "enter_name":
                if result is None:
                    await Events._cancel(manager)
                    return
                form.name = result
                await manager.start(
                    PromptSG.main,
                    data={
                        "intent": "enter_description",
                        "input": PromptDialogStartData("a description", can_skip=True),
                    },
                    show_mode=ShowMode.SEND,
                )
            case "enter_description":
                if result is None:
                    await Events._cancel(manager)
                    return
                form.period = result
                await manager.start(
                    CreateOrderSG.first,
                    data={"intent": "create_order", "input": CreateOrderStartData(manager.dialog_data["user_id"])},
                    show_mode=ShowMode.SEND,
                )
            case "create_order":
                if not result[0]:
                    await Events._cancel(manager)
                    return
                form.order_id = result[1]
                await manager.done((True, form), ShowMode.SEND)


create_manual_task_dialog = Dialog(
    Window(
        state=CreateManualTaskSG.main,
    ),
    on_start=Events.on_start,
    on_process_result=Events.on_process_result,
)
