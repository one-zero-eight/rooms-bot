from aiogram_dialog import ShowMode, DialogManager, Dialog, Window

from src.bot.dialogs.dialog_communications import PromptDialogStartData, CreateRuleForm
from src.bot.dialogs.states import PromptSG, CreateRuleSG


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        manager.dialog_data["form"] = CreateRuleForm()
        await manager.start(
            PromptSG.main,
            data={
                "intent": "enter_name",
                "input": PromptDialogStartData("a name for a rule"),
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
        form: CreateRuleForm = manager.dialog_data["form"]
        match start_data["intent"]:
            case "enter_name":
                if result is None:
                    await Events._cancel(manager)
                    return
                form.name = result
                await Events._prompt_step("enter_text", PromptDialogStartData("a text"), manager)
            case "enter_text":
                if result is None:
                    await Events._cancel(manager)
                    return
                form.text = result
                await manager.event.bot.send_message(manager.event.chat.id, "Created")
                await manager.done((True, form), ShowMode.SEND)


create_rule_dialog = Dialog(
    Window(
        state=CreateRuleSG.main,
    ),
    on_start=Events.on_start,
    on_process_result=Events.on_process_result,
)
