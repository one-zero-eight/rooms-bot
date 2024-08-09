from aiogram_dialog import ShowMode, DialogManager, Dialog, Window

from src.bot.dialogs.dialog_communications import PromptDialogStartData, CreateManualTaskForm
from src.bot.dialogs.states import PromptSG, CreateManualTaskSG, OrderSelectionSG


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
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
    async def on_process_result(start_data: dict, result: str | None, manager: DialogManager):
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


create_manual_task_dialog = Dialog(
    Window(
        state=CreateManualTaskSG.main,
    ),
    on_start=Events.on_start,
    on_process_result=Events.on_process_result,
)
