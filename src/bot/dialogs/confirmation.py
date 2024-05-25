from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Row, Select
from aiogram_dialog.widgets.text import Format

from src.bot.dialogs.dialog_communications import ConfirmationDialogStartData
from src.bot.dialogs.states import ConfirmationSG


async def on_start(start_data: dict, manager: DialogManager):
    args: ConfirmationDialogStartData = start_data["input"]
    manager.dialog_data["confirmation"] = args


async def getter(dialog_manager: DialogManager, **kwargs):
    confirmation: ConfirmationDialogStartData = dialog_manager.dialog_data["confirmation"]
    return {
        "question": confirmation.question,
    }


async def on_select(callback: CallbackQuery, select, manager: DialogManager, item_id: str):
    confirmation: ConfirmationDialogStartData = manager.dialog_data["confirmation"]
    confirmed = item_id == confirmation.yes_button
    answer = confirmation.yes_message if confirmed else confirmation.no_message
    if answer is not None:
        await callback.bot.send_message(callback.message.chat.id, answer)
    await manager.done(confirmed, show_mode=ShowMode.NO_UPDATE)


confirmation_dialog = Dialog(
    Window(
        Format("{question}"),
        Row(
            Select(
                Format("{item}"),
                items=["Yes", "No"],
                item_id_getter=str,
                on_click=on_select,
                id="select",
            )
        ),
        getter=getter,
        state=ConfirmationSG.main,
    ),
    on_start=on_start,
)
