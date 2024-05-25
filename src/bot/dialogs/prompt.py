from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from src.bot.dialogs.dialog_communications import PromptDialogStartData
from src.bot.dialogs.states import PromptSG


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        args: PromptDialogStartData = start_data["input"]
        manager.dialog_data["args"] = args

    @staticmethod
    async def on_cancel(callback: CallbackQuery, widget, manager: DialogManager):
        await callback.bot.send_message(callback.message.chat.id, manager.dialog_data["args"].cancel_message)
        await manager.done(None, show_mode=ShowMode.NO_UPDATE)

    @staticmethod
    async def on_input(message: Message, widget, manager: DialogManager, text: str):
        if not manager.dialog_data["args"].validate(text):
            return
        await manager.done(text, show_mode=ShowMode.NO_UPDATE)


async def getter(dialog_manager: DialogManager, **kwargs):
    dialog_args: PromptDialogStartData = dialog_manager.dialog_data["args"]
    return {
        "message": dialog_args.prompt,
        "cancel_button": dialog_args.cancel_button,
    }


prompt_dialog = Dialog(
    Window(
        Format("{message}"),
        Button(Format("{cancel_button}"), id="cancel_button", on_click=Events.on_cancel),
        TextInput("input_name", on_success=Events.on_input),
        state=PromptSG.main,
        getter=getter,
    ),
    on_start=Events.on_start,
)
