from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import SwitchTo, Button, Group, Select, Cancel
from aiogram_dialog.widgets.text import Format, Const, Jinja

from src.api import client
from src.api.schemas.method_input_schemas import CreateRuleBody
from src.api.schemas.method_output_schemas import RuleInfo
from src.bot.dialogs.dialog_communications import CreateRuleForm, ConfirmationDialogStartData
from src.bot.dialogs.states import RulesSG, CreateRuleSG, ConfirmationSG
from src.bot.utils import select_finder


class RulesWindowConsts:
    HEADER_TEXT = "Rules:\n"
    NEW_RULE_BUTTON_TEXT = "Add a new rule"
    RULE_FORMAT = "<b>{{rule.name}}</b>\n\n{{rule.text}}"
    DELETE_RULE_BUTTON_TEXT = "Delete"

    BACK_BUTTON_ID = "back_button"
    NEW_RULE_BUTTON_ID = "new_rule_button"
    RULE_SELECT_ID = "rule_select"
    DELETE_RULE_BUTTON_ID = "delete_button"


class Loader:
    @staticmethod
    async def load_rules(manager: DialogManager):
        data = await client.get_rules(manager.event.from_user.id)
        manager.dialog_data["rules"] = data


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        await Loader.load_rules(manager)

    @staticmethod
    @select_finder("rules")
    async def on_select_rule(callback: CallbackQuery, widget, manager: DialogManager, rule: RuleInfo):
        manager.dialog_data["current_rule"] = rule
        await manager.switch_to(
            RulesSG.view,
        )

    @staticmethod
    async def on_create_rule(callback: CallbackQuery, widget, manager: DialogManager):
        await manager.start(
            data={"intent": "create_rule"},
            state=CreateRuleSG.main,
            show_mode=ShowMode.SEND,
        )

    @staticmethod
    async def on_delete_rule(callback: CallbackQuery, widget, manager: DialogManager):
        await manager.start(
            data={
                "intent": "delete_rule",
                "input": ConfirmationDialogStartData("delete the rule", yes_message="The rule has been deleted"),
            },
            state=ConfirmationSG.main,
            show_mode=ShowMode.SEND,
        )

    @staticmethod
    async def on_process_result(start_data: dict, result: tuple[bool, CreateRuleForm], manager: DialogManager):
        if not isinstance(start_data, dict):
            return

        if start_data["intent"] == "create_rule":
            if not result[0]:
                return

            form: CreateRuleForm = result[1]
            await client.create_rule(CreateRuleBody(name=form.name, text=form.text), manager.event.from_user.id)
            await Loader.load_rules(manager)
            # no update is required because on_process happens before the dialog is re-rendered
        elif start_data["intent"] == "delete_rule":
            if result:
                user_id = manager.event.from_user.id
                rule: RuleInfo = manager.dialog_data["current_rule"]
                await client.delete_rule(rule.id, user_id)
                await Loader.load_rules(manager)
                # Here aiogram-dialog only changes an internal state variable.
                # To redraw (send) message, an explicit show() is required.
                await manager.switch_to(RulesSG.list)
                await manager.show(ShowMode.SEND)
                return
            await manager.show(ShowMode.SEND)


async def list_getter(dialog_manager: DialogManager, **kwargs):
    rules: list[RuleInfo] = dialog_manager.dialog_data["rules"]
    return {
        "rules": rules,
    }


async def view_getter(dialog_manager: DialogManager, **kwargs):
    rule: RuleInfo = dialog_manager.dialog_data["current_rule"]
    return {
        "rule": rule,
    }


rules_dialog = Dialog(
    # Rules list
    Window(
        Const(RulesWindowConsts.HEADER_TEXT),
        Group(
            Select(
                Format("{item.name}"),
                id=RulesWindowConsts.RULE_SELECT_ID,
                item_id_getter=lambda item: item.id,
                items="rules",
                on_click=Events.on_select_rule,
            ),
            width=2,
        ),
        Button(
            Const(RulesWindowConsts.NEW_RULE_BUTTON_TEXT),
            id=RulesWindowConsts.NEW_RULE_BUTTON_ID,
            on_click=Events.on_create_rule,
        ),
        Cancel(
            Const("◀️ Back"),
            RulesWindowConsts.BACK_BUTTON_ID,
        ),
        state=RulesSG.list,
        getter=list_getter,
    ),
    # View rule
    Window(
        Jinja(RulesWindowConsts.RULE_FORMAT),
        Button(
            Const(RulesWindowConsts.DELETE_RULE_BUTTON_TEXT),
            id=RulesWindowConsts.DELETE_RULE_BUTTON_ID,
            on_click=Events.on_delete_rule,
        ),
        SwitchTo(
            Const("◀️ Back"),
            id=RulesWindowConsts.BACK_BUTTON_ID,
            state=RulesSG.list,
        ),
        parse_mode="HTML",
        state=RulesSG.view,
        getter=view_getter,
    ),
    on_start=Events.on_start,
    on_process_result=Events.on_process_result,
)
