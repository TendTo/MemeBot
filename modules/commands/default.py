"""Handles the default commands /start /help /settings"""
from typing import Tuple
from random import randint
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext
import requests
from modules.commands.general_command import get_message_info, get_callback_info
from modules.data.data_reader import read_md


def start_cmd(update: Update, context: CallbackContext):
    """Handles the /start command

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)
    text = read_md("default_start")
    info['bot'].send_message(chat_id=info['chat_id'],
                             message_id=info['message_id'],
                             text=text,
                             parse_mode=ParseMode.MARKDOWN_V2)


def help_cmd(update: Update, context: CallbackContext):
    """Handles the /help command

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)
    text = read_md("default_help")
    info['bot'].send_message(chat_id=info['chat_id'],
                             message_id=info['message_id'],
                             text=text,
                             parse_mode=ParseMode.MARKDOWN_V2)


def settings_cmd(update: Update, context: CallbackContext):
    """Handles the /settings command

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)

    keyboard = [[]]
    keyboard.append([
        InlineKeyboardButton(" Sei ghei? ", callback_data="settings_sei_ghei"),
        InlineKeyboardButton(" Autodistruggiti ", callback_data="settings_autodistruggiti"),
    ])
    keyboard.append([
        InlineKeyboardButton(" Foto cane ", callback_data="settings_foto_cane"),
        InlineKeyboardButton(" Lancia dado minnigo ", callback_data="settings_lancia_dado")
    ])

    info['bot'].send_message(chat_id=info['chat_id'],
                             message_id=info['message_id'],
                             text="***Opzioni:***",
                             reply_markup=InlineKeyboardMarkup(keyboard),
                             parse_mode=ParseMode.MARKDOWN_V2)


def settings_callback(update: Update, context: CallbackContext):
    """Passes the settings callback to the correct handler

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_callback_info(update, context)
    data = update.callback_query.data
    reply = None
    try:
        reply = globals()[f'{data}_callback'](update, context)  # call the correct function based on it's name
    except NameError:
        print("[error] setting_callback: the function corrisponding to this callback_data was not found")
        print(f"callback_data: {data}")

    if reply and reply[0]:  # if a reply is to be send, edit the menu with the reply
        info['bot'].edit_message_text(chat_id=info['chat_id'],
                                      message_id=info['message_id'],
                                      text=reply[0],
                                      reply_markup=reply[1],
                                      parse_mode=ParseMode.MARKDOWN_V2)


# region utility settings_callback
def settings_sei_ghei_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup]:
    """Handles the settings_sei_ghei callback

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup]: text and InlineKeyboardMarkup needed that make up the reply
    """
    text = f"No, ma è chiaro che {update.callback_query.from_user.first_name} è bestia assai\n"
    return text, None


def settings_foto_cane_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup]:
    """Handles the settings_foto_cane callback

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup]: text and InlineKeyboardMarkup needed that make up the reply
    """
    text = "Eccoti una bella foto di un cane random\n"\
        f"[link]({requests.get('https://random.dog/woof.json').json()['url']})"
    return text, None


def settings_autodistruggiti_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup]:
    """Handles the settings_autodistruggiti callback

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup]: text and InlineKeyboardMarkup needed that make up the reply
    """
    text = "no"
    return text, None


def settings_lancia_dado_callback(update: Update, context: CallbackContext) -> Tuple[str, InlineKeyboardMarkup]:
    """Handles the settings_lancia_dado callback

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        Tuple[str, InlineKeyboardMarkup]: text and InlineKeyboardMarkup needed that make up the reply
    """
    text = f"Hai lanciato un 🎲\nIl risultato è {randint(1, 6)}"
    return text, None
    # endregion
